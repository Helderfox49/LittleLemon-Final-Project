from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User, Group

from .permissions import IsManager
from .serializers import UserSerializer


# Class View for managing user groups (Manager Group)
class ManagerUserGroupView(APIView):
    def get_permissions(self):
        return ([IsManager()])
    
    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        serializers = UserSerializer(managers, many=True)
        return Response(serializers.data)

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
