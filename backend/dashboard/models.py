from django.db import models
from django.utils import timezone
from profiles.models import Profile
from django.contrib.postgres.fields import ArrayField

class ViewHistory(models.Model):
    time = models.CharField(max_length=50)
    count = models.IntegerField()

    class Meta:
        managed = False  # This model is for response structure only

class ProfilePreviewCard(models.Model):
    profileID = models.IntegerField()
    isStartup = models.BooleanField()
    name = models.CharField(max_length=100)
    occupation = models.CharField(max_length=500)
    avatar = models.TextField(null=True)
    tags = ArrayField(models.CharField(max_length=50), size=30)

    class Meta:
        managed = False  # This model is for response structure only

class DashboardView(models.Model):
    viewedCount = models.IntegerField()
    viewedHistory = models.ManyToManyField(ViewHistory)
    connectRequestCount = models.IntegerField()
    matchedProfilesCount = models.IntegerField()
    sampleProfiles = models.ManyToManyField(ProfilePreviewCard)

    class Meta:
        managed = False  # This model is for response structure only