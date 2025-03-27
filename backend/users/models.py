from datetime import datetime

from mongoengine import (
    Document,
    StringField,
    EmailField,
    DateTimeField,
    BooleanField,
    IntField,
    DictField,
)


class User(Document):
    """
    User model for PixelSeek application.
    This model stores user information and authentication details.
    """
    email = EmailField(required=True, unique=True)
    username = StringField(max_length=100, required=True, unique=True)
    full_name = StringField(max_length=200)

    # SSO fields
    auth_provider = StringField(choices=['google', 'wechat', 'email'], default='email')
    auth_provider_id = StringField()

    # Account status
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_verified = BooleanField(default=False)

    # Subscription and credits
    subscription_tier = StringField(choices=['free', 'basic', 'premium'], default='free')
    credits_balance = IntField(default=0)

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()

    # Search preferences
    search_preferences = DictField()

    meta = {
        'indexes':    [
            'email',
            'username',
            'auth_provider_id',
            'subscription_tier'
        ],
        'collection': 'users'
    }

    def __str__(self):
        return self.username

    # Django authentication compatibility properties
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_username(self):
        return self.username
