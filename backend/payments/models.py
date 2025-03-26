from mongoengine import Document, StringField, FloatField, DateTimeField, ReferenceField, ListField, DictField
from datetime import datetime
from users.models import User

class Order(Document):
    """
    Model for tracking customer orders in the PixelSeek platform.
    """
    user = ReferenceField(User, required=True)
    
    # Order details
    order_number = StringField(required=True, unique=True)
    items = ListField(DictField())  # [{type: 'subscription'/'credits', quantity: int, unit_price: float}]
    total_amount = FloatField(required=True)
    currency = StringField(default='USD')
    
    # Status tracking
    status = StringField(choices=['pending', 'paid', 'cancelled', 'refunded'], default='pending')
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    paid_at = DateTimeField()
    
    meta = {
        'indexes': ['user', 'order_number', 'status', 'created_at'],
        'collection': 'orders'
    }
    
    def __str__(self):
        return f"Order {self.order_number} ({self.status})"


class Payment(Document):
    """
    Model for tracking payment transactions.
    """
    order = ReferenceField(Order, required=True)
    user = ReferenceField(User, required=True)
    
    # Payment details
    amount = FloatField(required=True)
    currency = StringField(default='USD')
    payment_method = StringField(choices=['credit_card', 'wechat', 'alipay', 'paypal'])
    
    # Transaction info
    transaction_id = StringField()
    provider_reference = StringField()  # External payment provider reference
    
    # Status
    status = StringField(choices=['pending', 'completed', 'failed', 'refunded'], default='pending')
    error_message = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    
    meta = {
        'indexes': ['order', 'user', 'transaction_id', 'status', 'created_at'],
        'collection': 'payments'
    }
    
    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.order_number}"


class Refund(Document):
    """
    Model for tracking refunds.
    """
    payment = ReferenceField(Payment, required=True)
    order = ReferenceField(Order, required=True)
    user = ReferenceField(User, required=True)
    
    # Refund details
    amount = FloatField(required=True)
    reason = StringField()
    
    # Transaction info
    refund_transaction_id = StringField()
    provider_reference = StringField()
    
    # Status
    status = StringField(choices=['pending', 'completed', 'failed'], default='pending')
    error_message = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    
    meta = {
        'indexes': ['payment', 'order', 'user', 'status', 'created_at'],
        'collection': 'refunds'
    }
    
    def __str__(self):
        return f"Refund {self.refund_transaction_id} for Payment {self.payment.transaction_id}" 