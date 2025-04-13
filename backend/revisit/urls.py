from django.urls import path
from .views import GetSavedProfilesView, GetSkippedProfilesView, GetViewedProfilesView

urlpatterns = [
    path('getSaved/', GetSavedProfilesView.as_view(), name='get_saved_profiles'),
    path('getSkipped/', GetSkippedProfilesView.as_view(), name='get_skipped_profiles'),
    path('getViewed/', GetViewedProfilesView.as_view(), name='get_viewed_profiles'),
] 