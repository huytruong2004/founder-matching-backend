from django.db import models
from profiles.models import Profile

class SavedProfiles(models.Model):
    saveID = models.AutoField(db_column='SaveID', primary_key=True)
    savedFromProfileID = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='SavedFromProfileID',
        related_name='saved_from_profiles'
    )
    savedToProfileID = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='SavedToProfileID',
        related_name='saved_to_profiles'
    )
    savedAt = models.DateTimeField(db_column='SavedAt')

    class Meta:
        managed = False
        db_table = 'SavedProfiles'
        ordering = ['-savedAt']  # Order by most recent first

class SkippedProfiles(models.Model):
    skipID = models.AutoField(db_column='SkipID', primary_key=True)
    skippedFromProfileID = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='SkippedFromProfileID',
        related_name='skipped_from_profiles'
    )
    skippedToProfileID = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='SkippedToProfileID',
        related_name='skipped_to_profiles'
    )
    skippedAt = models.DateTimeField(db_column='SkippedAt')

    class Meta:
        managed = False
        db_table = 'SkippedProfiles'
        ordering = ['-skippedAt']  # Order by most recent first

class ProfileViews(models.Model):
    viewID = models.AutoField(db_column='ViewID', primary_key=True)
    fromProfileID = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='FromProfileID',
        related_name='viewed_from_profiles'
    )
    toProfileID = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='ToProfileID',
        related_name='viewed_to_profiles'
    )
    viewedAt = models.DateTimeField(db_column='ViewedAt')

    class Meta:
        managed = False
        db_table = 'ProfileViews'
        ordering = ['-viewedAt']  # Order by most recent first
