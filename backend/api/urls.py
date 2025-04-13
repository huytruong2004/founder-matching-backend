from django.urls import path
from .views import test_api_view, ProtectedDashboardView

urlpatterns = [
    path('test/', test_api_view, name='test_api'),
    path("protected-dashboard/", ProtectedDashboardView.as_view(), name="protected_dashboard"),
]