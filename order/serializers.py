from asyncore import write
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_title =serializers.ReadOnlyField(source='product.title')
    product = serializers.IntegerField(write_only=True)
    # product = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = OrderItem
        fields =('product', 'quantity', 'product_title')
    
    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr.pop('product')
        return repr


class OrdeSerializer(serializers.ModelSerializer):
    position = OrderItemSerializer(write_only=True, many=True)
    status = serializers.CharField(read_only=True)
    user = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = Order
        fields = ('id', 'created_at', 'position', 'status', 'user')

    def create(self, validated_data):
        products = validated_data.pop('position')
        user = self.context.get('request').user
        order = Order.objects.create(user=user, status='open')
        for prod in products:
            product = prod['product']
            quantity = prod['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=quantity)
        return order

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['products'] = OrderItemSerializer(instance.items.all(), many=True) .data
        return repr