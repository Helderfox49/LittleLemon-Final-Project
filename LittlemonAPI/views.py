from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework import status, generics
from django.contrib.auth.models import User, Group
from django.db import transaction
from decimal import Decimal
from datetime import datetime

from .utils import is_user_in_group
from .permissions import IsManager, IsCustomer, IsDeliveryCrew, IsCustomerOrManagerOrDeliveryCrew, IsManagerOrDeliveryCrew
from .serializers import UserSerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .models import MenuItem, Cart, Category, Order, OrderItem


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
    

# Class View for managing Orders
class OrderCustomerView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsCustomerOrManagerOrDeliveryCrew()]
        elif self.request.method == 'POST':
            return [IsCustomer()]
        elif self.request.method in ['DELETE', 'PUT']:
            return [IsManager()]
        elif self.request.method == 'PATCH':
            return [IsManagerOrDeliveryCrew()]
        return []
         
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('orderId') 
        current_user = request.user

        if current_user.groups.filter(name="Customer").exists(): # If user is Customer
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)

                    if order.user != current_user:
                        return Response({"message": "You don't have acces to this order. You can only access Your order"}, status.HTTP_403_FORBIDDEN)

                    order_items = OrderItem.objects.filter(order=order).select_related('menuitem')
                    serializer = OrderItemSerializer(order_items, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                except Order.DoesNotExist:
                    return Response({"message": "Order not found"}, status.HTTP_404_NOT_FOUND)
            else:   
                orders = Order.objects.filter(user=request.user)
            
        elif current_user.groups.filter(name="Manager").exists(): # If user is Manager
            orders = Order.objects.all().select_related('user')
        
        elif current_user.groups.filter(name="Delivery Crew").exists(): # If User is from Delivery Crew
            orders = Order.objects.filter(delivery_crew=request.user)
            
        serializer = OrderSerializer(orders, many=True)        
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Get current user
        current_user = request.user

        # Savoing point for rollback
        sid = transaction.savepoint()

        try:
            # Get items on cart from the current user
            cart_items = Cart.objects.filter(user=current_user).select_related('menuitem')
            if not cart_items.exists():
                transaction.savepoint_rollback(sid)
                return Response({'message': 'Empty Card.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create new order table
            new_order = Order.objects.create(
                user= current_user,
                status= False,
                total= 0,
                date= datetime.now().date()
            )

            # For each cart item : create a new record in OrderItem table
            total=0 # Total variable to store the total price of an order
            for item in cart_items:
                item_dict = {
                    'order' : new_order,
                    'menuitem' : item.menuitem,
                    'quantity' : item.quantity,
                    'unit_price' : item.unit_price,
                    'price' : item.price
                }
                total += item.price
                OrderItem.objects.create(**item_dict)

            # Updating the total in the Order
            new_order.total = total
            new_order.save()

            # Flushing the cart of the user
            cart_items.delete()

            # Display the results
            serializer = OrderSerializer(new_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            transaction.savepoint_rollback(sid)
            return Response({'message': f"An Error Occured: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, *args, **kwargs):
        order_id = kwargs.get('orderId')
        if not order_id:
            return Response({'message': f"You need to specify an Order"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                order = Order.objects.get(id=order_id)
                order.delete()
                return Response("", status=status.HTTP_204_NO_CONTENT)
            except Order.DoesNotExist:
                return Response({'message': f"Order not Found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get('orderId')
        status_value = bool(int(request.data.get('status')))
        delivery_crew_id = request.data.get('delivery_crew_id')
        current_user = request.user

        if not order_id:
            return Response({'message': "You need to specify an order"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'message': "Order Not Found"}, status=status.HTTP_404_NOT_FOUND)

        # Cas 1 : Manager peut assigner un livreur
        if is_user_in_group(current_user, "Manager") and delivery_crew_id:
            try:
                delivery_user = User.objects.get(id=delivery_crew_id)
                order.delivery_crew = delivery_user
                order.save()
                serializer = OrderSerializer(order)
                return Response({'message': "Delivery user assigned", "order": serializer.data}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'message': "Delivery User Not Found"}, status=status.HTTP_404_NOT_FOUND)

        # Cas 2 : Manager ou livreur peut mettre à jour le statut
        if is_user_in_group(current_user, "Manager") or is_user_in_group(current_user, "Delivery Crew"):
            if order.delivery_crew != current_user and not is_user_in_group(current_user, "Manager"):
                return Response({'message': "You can't modify this order"}, status=status.HTTP_403_FORBIDDEN)
            if status_value is not None:
                order.status = status_value
                print(bool(status_value))
                order.save()
                serializer = OrderSerializer(order)
                return Response({'message': "Order status updated", "order": serializer.data}, status=status.HTTP_200_OK)

        return Response({'message': "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
            
    def put(self, request, *args, **kwargs):
        order_id = kwargs.get('orderId')
 
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'message': "Order Not Found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "Order updated successfully", "order": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)