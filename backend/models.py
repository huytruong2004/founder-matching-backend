# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Achievement(models.Model):
    achievementid = models.AutoField(db_column='AchievementID', primary_key=True)  # Field name made lowercase.
    profileowner = models.ForeignKey('Profile', models.DO_NOTHING, db_column='ProfileOwner')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=200)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Achievement'


class Achievementtaginstances(models.Model):
    achievementid = models.OneToOneField(Achievement, models.DO_NOTHING, db_column='AchievementID', primary_key=True)  # Field name made lowercase. The composite primary key (AchievementID, TagID) found, that is not supported. The first column is selected.
    tagid = models.ForeignKey('Tags', models.DO_NOTHING, db_column='TagID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AchievementTagInstances'
        unique_together = (('achievementid', 'tagid'),)


class Certificate(models.Model):
    certificateid = models.AutoField(db_column='CertificateID', primary_key=True)  # Field name made lowercase.
    profileowner = models.ForeignKey('Profile', models.DO_NOTHING, db_column='ProfileOwner')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=200)  # Field name made lowercase.
    skill = models.CharField(db_column='Skill', max_length=100, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    gpa = models.FloatField(db_column='GPA', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Certificate'


class Certificatetaginstances(models.Model):
    certificateid = models.OneToOneField(Certificate, models.DO_NOTHING, db_column='CertificateID', primary_key=True)  # Field name made lowercase. The composite primary key (CertificateID, TagID) found, that is not supported. The first column is selected.
    tagid = models.ForeignKey('Tags', models.DO_NOTHING, db_column='TagID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CertificateTagInstances'
        unique_together = (('certificateid', 'tagid'),)


class Countries(models.Model):
    num_code = models.IntegerField(primary_key=True)
    alpha_2_code = models.CharField(max_length=2)
    alpha_3_code = models.CharField(max_length=3)
    en_short_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Countries'


class Experience(models.Model):
    experienceid = models.AutoField(db_column='ExperienceID', primary_key=True)  # Field name made lowercase.
    profileowner = models.ForeignKey('Profile', models.DO_NOTHING, db_column='ProfileOwner')  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=100)  # Field name made lowercase.
    role = models.CharField(db_column='Role', max_length=100, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=100, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Experience'


class Experiencetaginstances(models.Model):
    experienceid = models.OneToOneField(Experience, models.DO_NOTHING, db_column='ExperienceID', primary_key=True)  # Field name made lowercase. The composite primary key (ExperienceID, TagID) found, that is not supported. The first column is selected.
    tagid = models.ForeignKey('Tags', models.DO_NOTHING, db_column='TagID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ExperienceTagInstances'
        unique_together = (('experienceid', 'tagid'),)


class Jobposition(models.Model):
    jobpositionid = models.AutoField(db_column='JobPositionID', primary_key=True)  # Field name made lowercase.
    profileowner = models.ForeignKey('Profile', models.DO_NOTHING, db_column='ProfileOwner')  # Field name made lowercase.
    jobtitle = models.CharField(db_column='JobTitle', max_length=100)  # Field name made lowercase.
    isopening = models.BooleanField(db_column='IsOpening', blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=100, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=10000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'JobPosition'


class Jobpositiontaginstances(models.Model):
    jobpositionid = models.OneToOneField(Jobposition, models.DO_NOTHING, db_column='JobPositionID', primary_key=True)  # Field name made lowercase. The composite primary key (JobPositionID, TagID) found, that is not supported. The first column is selected.
    tagid = models.ForeignKey('Tags', models.DO_NOTHING, db_column='TagID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'JobPositionTagInstances'
        unique_together = (('jobpositionid', 'tagid'),)


class Matching(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    candidateprofileid = models.ForeignKey('Profile', models.DO_NOTHING, db_column='CandidateProfileID')  # Field name made lowercase.
    startupprofileid = models.ForeignKey('Profile', models.DO_NOTHING, db_column='StartupProfileID', related_name='matching_startupprofileid_set')  # Field name made lowercase.
    candidatestatus = models.TextField(db_column='CandidateStatus')  # Field name made lowercase. This field type is a guess.
    startupstatus = models.TextField(db_column='StartupStatus')  # Field name made lowercase. This field type is a guess.
    ismatched = models.BooleanField(db_column='IsMatched')  # Field name made lowercase.
    matchdate = models.DateTimeField(db_column='MatchDate')  # Field name made lowercase.
    candidatenotification = models.IntegerField(db_column='CandidateNotification', blank=True, null=True)  # Field name made lowercase.
    startupnotification = models.IntegerField(db_column='StartupNotification', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Matching'


class Notification(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    recipient = models.ForeignKey('Useraccount', models.DO_NOTHING, db_column='Recipient')  # Field name made lowercase.
    data = models.CharField(db_column='Data', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    read = models.BooleanField(db_column='Read')  # Field name made lowercase.
    createddatetime = models.DateTimeField(db_column='CreatedDateTime')  # Field name made lowercase.
    isstartupnotified = models.BooleanField(db_column='IsStartupNotified')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Notification'


class Profile(models.Model):
    profileid = models.AutoField(db_column='ProfileID', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('Useraccount', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    isstartup = models.BooleanField(db_column='IsStartup')  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=100)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=255)  # Field name made lowercase.
    industry = models.CharField(db_column='Industry', max_length=100)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='PhoneNumber', max_length=20, blank=True, null=True)  # Field name made lowercase.
    country = models.CharField(db_column='Country', max_length=100, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    linkedinurl = models.CharField(db_column='LinkedInURL', unique=True, max_length=255, blank=True, null=True)  # Field name made lowercase.
    slogan = models.CharField(db_column='Slogan', max_length=255, blank=True, null=True)  # Field name made lowercase.
    websitelink = models.CharField(db_column='WebsiteLink', max_length=255, blank=True, null=True)  # Field name made lowercase.
    avatar = models.TextField(db_column='Avatar', blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    gender = models.TextField(db_column='Gender', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    hobbyinterest = models.CharField(db_column='HobbyInterest', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    education = models.CharField(db_column='Education', max_length=500, blank=True, null=True)  # Field name made lowercase.
    dateofbirth = models.DateTimeField(db_column='DateOfBirth', blank=True, null=True)  # Field name made lowercase.
    currentstage = models.CharField(db_column='CurrentStage', max_length=2000, blank=True, null=True)  # Field name made lowercase.
    aboutus = models.CharField(db_column='AboutUs', max_length=5000, blank=True, null=True)  # Field name made lowercase.
    statement = models.CharField(db_column='Statement', max_length=5000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Profile'


class Profileprivacysettings(models.Model):
    profileid = models.OneToOneField(Profile, models.DO_NOTHING, db_column='ProfileID', primary_key=True)  # Field name made lowercase.
    genderprivacy = models.TextField(db_column='GenderPrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    industryprivacy = models.TextField(db_column='IndustryPrivacy')  # Field name made lowercase. This field type is a guess.
    emailprivacy = models.TextField(db_column='EmailPrivacy')  # Field name made lowercase. This field type is a guess.
    phonenumberprivacy = models.TextField(db_column='PhoneNumberPrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    countryprivacy = models.TextField(db_column='CountryPrivacy')  # Field name made lowercase. This field type is a guess.
    cityprivacy = models.TextField(db_column='CityPrivacy')  # Field name made lowercase. This field type is a guess.
    universityprivacy = models.TextField(db_column='UniversityPrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    linkedinurlprivacy = models.TextField(db_column='LinkedInURLPrivacy')  # Field name made lowercase. This field type is a guess.
    sloganprivacy = models.TextField(db_column='SloganPrivacy')  # Field name made lowercase. This field type is a guess.
    websitelinkprivacy = models.TextField(db_column='WebsiteLinkPrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    certificateprivacy = models.TextField(db_column='CertificatePrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    experienceprivacy = models.TextField(db_column='ExperiencePrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    hobbyinterestprivacy = models.TextField(db_column='HobbyInterestPrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    educationprivacy = models.TextField(db_column='EducationPrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    dateofbirthprivacy = models.TextField(db_column='DateOfBirthPrivacy', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    achievementprivacy = models.TextField(db_column='AchievementPrivacy')  # Field name made lowercase. This field type is a guess.

    class Meta:
        managed = False
        db_table = 'ProfilePrivacySettings'


class Profiletaginstances(models.Model):
    profileownerid = models.OneToOneField(Profile, models.DO_NOTHING, db_column='ProfileOwnerID', primary_key=True)  # Field name made lowercase. The composite primary key (ProfileOwnerID, TagID) found, that is not supported. The first column is selected.
    tagid = models.ForeignKey('Tags', models.DO_NOTHING, db_column='TagID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ProfileTagInstances'
        unique_together = (('profileownerid', 'tagid'),)


class Profileviews(models.Model):
    viewid = models.AutoField(db_column='ViewID', primary_key=True)  # Field name made lowercase.
    fromprofileid = models.ForeignKey(Profile, models.DO_NOTHING, db_column='FromProfileID', blank=True, null=True)  # Field name made lowercase.
    toprofileid = models.ForeignKey(Profile, models.DO_NOTHING, db_column='ToProfileID', related_name='profileviews_toprofileid_set', blank=True, null=True)  # Field name made lowercase.
    viewedat = models.DateTimeField(db_column='ViewedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ProfileViews'


class Savedprofiles(models.Model):
    saveid = models.AutoField(db_column='SaveID', primary_key=True)  # Field name made lowercase.
    savedfromprofileid = models.ForeignKey(Profile, models.DO_NOTHING, db_column='SavedFromProfileID')  # Field name made lowercase.
    savedtoprofileid = models.ForeignKey(Profile, models.DO_NOTHING, db_column='SavedToProfileID', related_name='savedprofiles_savedtoprofileid_set')  # Field name made lowercase.
    savedat = models.DateTimeField(db_column='SavedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SavedProfiles'


class Skippedprofiles(models.Model):
    skipid = models.AutoField(db_column='SkipID', primary_key=True)  # Field name made lowercase.
    skippedfromprofileid = models.ForeignKey(Profile, models.DO_NOTHING, db_column='SkippedFromProfileID')  # Field name made lowercase.
    skippedtoprofileid = models.ForeignKey(Profile, models.DO_NOTHING, db_column='SkippedToProfileID', related_name='skippedprofiles_skippedtoprofileid_set')  # Field name made lowercase.
    skippedat = models.DateTimeField(db_column='SkippedAt')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SkippedProfiles'


class Startupmembership(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    startupprofileid = models.ForeignKey(Profile, models.DO_NOTHING, db_column='StartupProfileID')  # Field name made lowercase.
    userid = models.ForeignKey('Useraccount', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    role = models.CharField(db_column='Role', max_length=100)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=2000, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StartupMembership'


class Tags(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=50)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Tags'


class Useraccount(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    clerkuserid = models.CharField(db_column='ClerkUserID', unique=True, max_length=255)  # Field name made lowercase.
    email = models.CharField(db_column='Email', unique=True, max_length=255)  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=50)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'UserAccount'
