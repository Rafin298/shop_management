# core/serializers.py
from rest_framework import serializers
from .models import User, Category, Product, Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id','username','password','email','role')
    def create(self, validated):
        user = User(
            username=validated['username'],
            email=validated.get('email'),
            role=validated['role']
        )
        user.set_password(validated['password'])
        user.save()
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','name')

class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.ReadOnlyField(source='seller.username')
    class Meta:
        model = Product
        fields = ('id','seller','category','name','description','price','stock')

class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    class Meta:
        model = OrderItem
        fields = ('id','product','product_detail','quantity','total_price')

class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='customer.username')
    items = OrderItemSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = Order
        fields = ('id','customer','created_at','payment_status','items','total_amount')

    def create(self, validated):
        items_data = validated.pop('items')
        order = Order.objects.create(**validated)
        for item in items_data:
            OrderItem.objects.create(order=order, **item)
        return order