from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    UserViewSet,
    CurrentUserView,
    google_login,
    google_callback,
    wechat_login,
    wechat_callback,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile endpoint
    path('me/', CurrentUserView.as_view(), name='current_user'),

    # SSO endpoints
    path('auth/google/login/', google_login, name='google_login'),
    path('auth/google/callback/', google_callback, name='google_callback'),
    path('auth/wechat/login/', wechat_login, name='wechat_login'),
    path('auth/wechat/callback/', wechat_callback, name='wechat_callback'),

    # Router URLs
    path('', include(router.urls)),
]
