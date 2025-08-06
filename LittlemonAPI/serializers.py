from rest_framework import serializers 
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User

from .models import MenuItem, Category, Cart


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'slug']


class MenuItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0.01)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

        extra_kwargs = {
            'title' : {
                'validators' : [UniqueValidator(queryset=MenuItem.objects.all())],
                'min_length' : 2,
                'max_length' : 255
            }
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField()

    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0.01)

    def validate_quantity(self, value):
        if (value < 1):
            raise serializers.ValidationError('Quantity should be at least 1')
        return value
    
    class Meta:
        model = Cart
        fields = ['user', 'user_id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price'] 
