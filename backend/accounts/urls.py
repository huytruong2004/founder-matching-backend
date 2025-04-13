from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserAccountViewSet, basename='useraccount')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', views.current_user, name='current-user'),
] 