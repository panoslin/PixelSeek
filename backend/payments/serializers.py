from rest_framework_mongoengine import serializers
from users.serializers import UserProfileSerializer
from .models import Order, Payment, Refund


class OrderSerializer(serializers.DocumentSerializer):
    """
    Serializer for the Order model with all fields.
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'paid_at']


class OrderCreateSerializer(serializers.DocumentSerializer):
    """
    Serializer for creating new orders.
    """
    class Meta:
        model = Order
        fields = ['items', 'currency']
        
    def validate(self, data):
        """
        Validate the order data, including calculating the total amount.
        """
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")
            
        # Calculate total amount based on items
        total_amount = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in items)
        if total_amount <= 0:
            raise serializers.ValidationError("Total order amount must be greater than zero.")
            
        # Add calculated values to the validated data
        data['total_amount'] = total_amount
        
        return data


class PaymentSerializer(serializers.DocumentSerializer):
    """
    Serializer for the Payment model.
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'completed_at']


class PaymentCreateSerializer(serializers.DocumentSerializer):
    """
    Serializer for creating new payments.
    """
    class Meta:
        model = Payment
        fields = ['order', 'payment_method', 'currency']


class RefundSerializer(serializers.DocumentSerializer):
    """
    Serializer for the Refund model.
    """
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Refund
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'completed_at']


class RefundCreateSerializer(serializers.DocumentSerializer):
    """
    Serializer for creating refund requests.
    """
    class Meta:
        model = Refund
        fields = ['payment', 'reason']
        
    def validate(self, data):
        """
        Validate the refund request, ensuring it's for a valid payment.
        """
        payment = data.get('payment')
        if payment and payment.status != 'completed':
            raise serializers.ValidationError("Can only refund completed payments.")
            
        # Set the refund amount to the payment amount (full refund)
        data['amount'] = payment.amount
        data['order'] = payment.order
        
        return data 