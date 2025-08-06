from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework import status, generics
from django.contrib.auth.models import User, Group
from decimal import Decimal

from .permissions import IsManager, IsCustomer, IsDeliveryCrew
from .serializers import UserSerializer, MenuItemSerializer, CartSerializer
from .models import MenuItem, Cart, Category


# Class View for managing menu Item
class MenuItemListCreateView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsManager(), IsAdminUser()]
        return []
    
    def post(self, request, *args, **kwargs):
        serializer_item = MenuItemSerializer(data=request.data)
        serializer_item.is_valid(raise_exception=True)
        serializer_item.save()
        return Response(data=serializer_item.data, status=status.HTTP_201_CREATED)


class MenuItemRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return ([IsManager()])
        return [IsCustomer(), IsManager()]


# Class View for managing Customer Cart
class CartCustomerView(APIView):
    def get_permissions(self):
        return ([IsCustomer()])
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('menuitem')
    
    def get(self, request, *args, **kwargs):
        cart_items = self.get_queryset()
        serializer = CartSerializer(cart_items, many=True)

        total = sum(item.price for item in cart_items)
        cart_data = {
            'items' : serializer.data,
            'total' : total
        }

        return Response(cart_data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        menuitem_id = request.data.get('menuitem_id')
        quantity =  request.data.get('quantity', 1)
        print(quantity)
        
        if not menuitem_id:
            return Response({"error": "menuitem_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "menuitem not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menuitem,
            defaults={
                'quantity': quantity,
                'unit_price': menuitem.price,
                'price': Decimal(str(menuitem.price)) * Decimal(quantity)
            }
        )

        if not created:
            cart_item.quantity += int(quantity)
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save() 

        serializer = CartSerializer(cart_item)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response({"message": "Cart Emptied"}, status=status.HTTP_204_NO_CONTENT)


# Class View for managing user groups (Manager Group)
class ManagerUserGroupView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return ([IsManager(), IsAdminUser()])
        return ([IsAdminUser()])
    
    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        group, _ = Group.objects.get_or_create(name='Manager')

        if not username:
            return Response(
                {"message": "Username is required"},
                status= status.HTTP_400_BAD_REQUEST
            )
        
        try: 
            user = User.objects.get(username=username)
            user.groups.add(group)
            return Response(
                {"message": f"User {username} added to the Manager group"},
                status= status.HTTP_201_CREATED
            )
        except User.DoesNotExist: 
            return Response({"message": "This User doesn't exit"}, status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('userId')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name='Manager')

            if not user.groups.filter(name='Manager').exists():
                return Response({"message": f"The user {user_id} don't belong to the Manager Group"}, status.HTTP_400_BAD_REQUEST)

            user.groups.remove(group)
            return Response({"message": f"The user {user_id} removed from Manager Group"}, status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status.HTTP_404_NOT_FOUND)


# Class View for managing user groups (Delivery Crew Group)
class DeliveryUserGroupView(APIView):
    def get_permissions(self):
        return ([IsManager()])
    
    def get(self, request, *args, **kwargs):
        delivery_user = User.objects.filter(groups__name='Delivery Crew')
        serializer = UserSerializer(delivery_user, many=True)
        return Response(serializer.data)
    
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        group, _ = Group.objects.get_or_create(name='Delivery Crew')

        if not username:
            return Response(
                {"message": "Username is required"},
                status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(username=username)
            user.groups.add(group)
            return Response(
                {"message": f"User {username} added to Delivery Group"},
                status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"message": f"User {username} not found"},
                status.HTTP_404_NOT_FOUND
            )
        
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get('userId')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name='Delivery Crew')

            if not user.groups.filter(name='Delivery Crew').exists():
                return Response({"message": f"The user {user_id} don't belong to the Delivery Crew Group"}, status.HTTP_400_BAD_REQUEST)

            user.groups.remove(group)
            return Response({"message": f"The user {user_id} removed from Delivery Crew Group"}, status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status.HTTP_404_NOT_FOUND)
    

# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsManager])
# def manager_list(request):
#     if request.user.groups.filter(name="Manager").exists():
#         managers = User.objects.filter(groups__name="Manager")
#         serializer = UserSerializer(managers, many=True)
#         return Response(serializer.data)
#     else:
#         return Response({"message": "You do not have permission to perform this action."}, 403)
