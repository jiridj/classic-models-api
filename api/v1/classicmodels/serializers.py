from rest_framework import serializers

from classicmodels.models import (
    Customer,
    Employee,
    Office,
    Order,
    Orderdetail,
    Payment,
    Product,
    ProductLine,
)


class ProductLineSerializer(serializers.ModelSerializer):
    """Product line category information"""
    
    class Meta:
        model = ProductLine
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    """Product catalog information"""
    
    class Meta:
        model = Product
        fields = "__all__"


class OfficeSerializer(serializers.ModelSerializer):
    """Company office locations"""
    
    class Meta:
        model = Office
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    """Employee information and hierarchy"""
    
    class Meta:
        model = Employee
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    """Customer information and contact details"""
    
    class Meta:
        model = Customer
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    """Customer payment records"""
    
    class Meta:
        model = Payment
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    """Customer order information"""
    
    class Meta:
        model = Order
        fields = "__all__"


class OrderdetailSerializer(serializers.ModelSerializer):
    """Order line items with product details"""
    
    class Meta:
        model = Orderdetail
        fields = "__all__"


