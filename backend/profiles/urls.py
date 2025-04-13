from django.urls import path
from .views import (
    CreateProfileView,
    GetUserProfilesView,
    GetCurrentUserProfileView,
    GetUserProfileByIdView,
    UpdateProfileView
)

urlpatterns = [
    path('create/', CreateProfileView.as_view(), name='create_profile'),
    path('getUserProfiles/', GetUserProfilesView.as_view(), name='get_user_profiles'),
    path('me/', GetCurrentUserProfileView.as_view(), name='get_current_user_profile'),
    path('me/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('<int:profileID>', GetUserProfileByIdView.as_view(), name='get_user_profile_by_id'),
] 