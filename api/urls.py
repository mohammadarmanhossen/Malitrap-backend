from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, InboxViewSet, EmailViewSet, send_test_email

router = DefaultRouter()
router.register(r'inboxes', InboxViewSet, basename='inbox')
router.register(r'emails', EmailViewSet, basename='email')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('send-test/', send_test_email, name='send_test_email'),
]
