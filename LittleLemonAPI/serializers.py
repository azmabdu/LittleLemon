from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField(method_name='get_slug', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

    def get_slug(self, category: Category):
        return category.slug

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    menuitem = serializers.StringRelatedField(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ['unit_price', 'price', 'user']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    status = serializers.BooleanField(read_only=True)
    total = serializers.IntegerField(read_only=True)
    delivery_crew = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.StringRelatedField(read_only=True)
    order_id = serializers.IntegerField(write_only=True)

    menuitem = serializers.StringRelatedField(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['order_id', 'order', 'menuitem_id', 'menuitem' ,'quantity']