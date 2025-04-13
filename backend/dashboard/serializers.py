from rest_framework import serializers
from .models import DashboardView, ViewHistory, ProfilePreviewCard

class ViewHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewHistory
        fields = ['time', 'count']

class ProfilePreviewCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePreviewCard
        fields = ['profileID', 'isStartup', 'name', 'occupation', 'avatar', 'tags']

class DashboardViewSerializer(serializers.ModelSerializer):
    viewedHistory = ViewHistorySerializer(many=True)
    sampleProfiles = ProfilePreviewCardSerializer(many=True)

    class Meta:
        model = DashboardView
        fields = ['viewedCount', 'viewedHistory', 'connectRequestCount', 'matchedProfilesCount', 'sampleProfiles'] 