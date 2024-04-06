from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta():
        model = Category
        fields = ['slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = "__all__"
        depth = 1


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class GroupSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username']


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'price']


class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']
        extra_kwars = {
            'quantity': {'min_value': 1},
        }


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)      
    class Meta:
        model = Order
        fields = "__all__"

