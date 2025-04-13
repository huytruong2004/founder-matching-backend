from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

class Countries(models.Model):
    num_code = models.IntegerField(primary_key=True)
    alpha_2_code = models.CharField(max_length=2)
    alpha_3_code = models.CharField(max_length=3)
    en_short_name = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'Countries'

class UserAccount(models.Model):
    userID = models.AutoField(db_column='UserID', primary_key=True)
    clerkUserID = models.CharField(db_column='ClerkUserID', unique=True, max_length=255)
    email = models.CharField(db_column='Email', unique=True, max_length=255)
    firstName = models.CharField(db_column='FirstName', max_length=50)
    lastName = models.CharField(db_column='LastName', max_length=50)

    class Meta:
        managed = False
        db_table = 'UserAccount'

class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    profileID = models.AutoField(db_column='ProfileID', primary_key=True)
    userID = models.ForeignKey(UserAccount, models.DO_NOTHING, db_column='UserID')
    isStartup = models.BooleanField(db_column='IsStartup')
    name = models.CharField(
        db_column='Name',
        max_length=100,
        validators=[RegexValidator(
            r'^[A-Za-z]+((\s)?((\'|\-|\.)?([A-Za-z])+))*$',
            'Invalid name format.'
        )]
    )
    email = models.CharField(
        db_column='Email',
        max_length=255,
        validators=[RegexValidator(
            r'^[^@\s]+@[^@\s]+\.[^@\s]+$',
            'Invalid email format.'
        )]
    )
    industry = models.CharField(
        db_column='Industry',
        max_length=100,
        validators=[RegexValidator(
            r'^[A-Za-z\s&,-]+$',
            'Invalid industry format.'
        )]
    )
    phoneNumber = models.CharField(
        db_column='PhoneNumber',
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'^\+[1-9]{1}[0-9]{3,14}$',
            'Invalid phone number format.'
        )]
    )
    country = models.CharField(
        db_column='Country',
        max_length=100,
        blank=True,
        null=True
    )
    city = models.CharField(
        db_column='City',
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'^[A-Za-z]+((\s)?((\'|\-|\.)?([A-Za-z])+))*$',
            'Invalid city format.'
        )]
    )
    linkedInURL = models.CharField(
        db_column='LinkedInURL',
        unique=True,
        max_length=255,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'^https?://(www\.)?linkedin\.com/.*$',
            'Invalid LinkedIn URL.'
        )]
    )
    slogan = models.CharField(db_column='Slogan', max_length=255, blank=True, null=True)
    websiteLink = models.CharField(
        db_column='WebsiteLink',
        max_length=255,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'(?:http[s]?://)?(?:www\.)?[-a-zA-Z0-9@%._\+~#=]{2,256}\.[a-z]{2,6}\b(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)',
            'Invalid website URL.'
        )]
    )
    avatar = models.TextField(
        db_column='Avatar',
        blank=True,
        null=True,
        help_text='Base64 encoded image data with format: data:image/[type];base64,[data]'
    )
    description = models.CharField(db_column='Description', max_length=5000, blank=True, null=True)
    gender = models.TextField(db_column='Gender', blank=True, null=True, choices=GENDER_CHOICES)
    hobbyInterest = models.CharField(db_column='HobbyInterest', max_length=500, blank=True, null=True)
    education = models.CharField(db_column='Education', max_length=500, blank=True, null=True)
    dateOfBirth = models.DateField(db_column='DateOfBirth', blank=True, null=True)
    currentStage = models.CharField(db_column='CurrentStage', max_length=255, blank=True, null=True)
    statement = models.CharField(db_column='Statement', max_length=1000, blank=True, null=True)
    aboutUs = models.CharField(db_column='AboutUs', max_length=5000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Profile'

class Experience(models.Model):
    experienceID = models.AutoField(db_column='ExperienceID', primary_key=True)
    profileOwner = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='ProfileOwner',
        related_name='experiences'
    )
    companyName = models.CharField(
        db_column='CompanyName',
        max_length=100,
        validators=[RegexValidator(
            r'^[A-Za-z0-9\s&\',.-]+$',
            'Invalid company name format.'
        )]
    )
    role = models.CharField(
        db_column='Role',
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'^[A-Za-z0-9\s&\',.-]+$',
            'Invalid role format.'
        )]
    )
    location = models.CharField(
        db_column='Location',
        max_length=100,
        blank=True,
        null=True
    )
    description = models.CharField(db_column='Description', max_length=2000, blank=True, null=True)
    startDate = models.DateField(db_column='StartDate', blank=True, null=True)
    endDate = models.DateField(db_column='EndDate', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Experience'

class Certificate(models.Model):
    certificateID = models.AutoField(db_column='CertificateID', primary_key=True)
    profileOwner = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='ProfileOwner',
        related_name='certificates'
    )
    name = models.CharField(
        db_column='Name',
        max_length=200,
        validators=[RegexValidator(
            r'^[A-Za-z0-9\s&\',.-]+$',
            'Invalid certificate name format.'
        )]
    )
    skill = models.CharField(
        db_column='Skill',
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'^[A-Za-z0-9\s&\',.-]+$',
            'Invalid skills format.'
        )]
    )
    description = models.CharField(db_column='Description', max_length=2000, blank=True, null=True)
    startDate = models.DateField(db_column='StartDate', blank=True, null=True)
    endDate = models.DateField(db_column='EndDate', blank=True, null=True)
    gpa = models.FloatField(
        db_column='GPA',
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(2147483647)
        ]
    )

    class Meta:
        managed = False
        db_table = 'Certificate'

class Achievement(models.Model):
    achievementID = models.AutoField(db_column='AchievementID', primary_key=True)
    profileOwner = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='ProfileOwner',
        related_name='achievements'
    )
    name = models.CharField(
        db_column='Name',
        max_length=200,
        validators=[RegexValidator(
            r'^[A-Za-z0-9\s&\',.-]+$',
            'Invalid achievement name format.'
        )]
    )
    description = models.CharField(db_column='Description', max_length=2000, blank=True, null=True)
    date = models.DateField(db_column='Date', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Achievement'

class ProfilePrivacySettings(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('connections', 'Connections'),
    ]

    profileID = models.OneToOneField(
        Profile,
        models.DO_NOTHING,
        db_column='ProfileID',
        primary_key=True
    )
    genderPrivacy = models.TextField(db_column='GenderPrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    industryPrivacy = models.TextField(db_column='IndustryPrivacy', choices=PRIVACY_CHOICES)
    emailPrivacy = models.TextField(db_column='EmailPrivacy', choices=PRIVACY_CHOICES)
    phoneNumberPrivacy = models.TextField(db_column='PhoneNumberPrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    countryPrivacy = models.TextField(db_column='CountryPrivacy', choices=PRIVACY_CHOICES)
    cityPrivacy = models.TextField(db_column='CityPrivacy', choices=PRIVACY_CHOICES)
    universityPrivacy = models.TextField(db_column='UniversityPrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    linkedInURLPrivacy = models.TextField(db_column='LinkedInURLPrivacy', choices=PRIVACY_CHOICES)
    sloganPrivacy = models.TextField(db_column='SloganPrivacy', choices=PRIVACY_CHOICES)
    websiteLinkPrivacy = models.TextField(db_column='WebsiteLinkPrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    certificatePrivacy = models.TextField(db_column='CertificatePrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    experiencePrivacy = models.TextField(db_column='ExperiencePrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    hobbyInterestPrivacy = models.TextField(db_column='HobbyInterestPrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    educationPrivacy = models.TextField(db_column='EducationPrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    dateOfBirthPrivacy = models.TextField(db_column='DateOfBirthPrivacy', blank=True, null=True, choices=PRIVACY_CHOICES)
    achievementPrivacy = models.TextField(db_column='AchievementPrivacy', choices=PRIVACY_CHOICES)

    class Meta:
        managed = False
        db_table = 'ProfilePrivacySettings'

class Tags(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    value = models.CharField(db_column='Value', max_length=50)
    description = models.CharField(db_column='Description', max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Tags'

class ProfileTagInstances(models.Model):
    profileOwnerID = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='ProfileOwnerID',
        primary_key=True,
        related_name='tags'
    )
    tagID = models.ForeignKey(
        Tags,
        models.DO_NOTHING,
        db_column='TagID'
    )

    class Meta:
        managed = False
        db_table = 'ProfileTagInstances'
        unique_together = (('profileOwnerID', 'tagID'),)

class JobPosition(models.Model):
    jobPositionID = models.AutoField(db_column='JobPositionID', primary_key=True)
    profileOwner = models.ForeignKey(
        Profile,
        models.DO_NOTHING,
        db_column='ProfileOwner',
        related_name='jobPositions'
    )
    jobTitle = models.CharField(
        db_column='JobTitle',
        max_length=100,
        validators=[RegexValidator(
            r'^[A-Za-z0-9\s&\',.-]+$',
            'Invalid job title format.'
        )]
    )
    isOpening = models.BooleanField(db_column='IsOpening', default=True)
    country = models.CharField(
        db_column='Country',
        max_length=100,
        validators=[RegexValidator(
            r'^[A-Za-z]+((\s)?((\'|\-|\.)?([A-Za-z])+))*$',
            'Invalid country format.'
        )]
    )
    city = models.CharField(
        db_column='City',
        max_length=100,
        blank=True,
        null=True,
        validators=[RegexValidator(
            r'^[A-Za-z]+((\s)?((\'|\-|\.)?([A-Za-z])+))*$',
            'Invalid city format.'
        )]
    )
    startDate = models.DateField(db_column='StartDate', blank=True, null=True)
    description = models.CharField(db_column='Description', max_length=10000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'JobPosition'

class JobPositionTagInstances(models.Model):
    jobPositionID = models.ForeignKey(
        JobPosition,
        models.DO_NOTHING,
        db_column='JobPositionID',
        primary_key=True,
        related_name='tags'
    )
    tagID = models.ForeignKey(
        Tags,
        models.DO_NOTHING,
        db_column='TagID'
    )

    class Meta:
        managed = False
        db_table = 'JobPositionTagInstances'
        unique_together = (('jobPositionID', 'tagID'),)

class Connection(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    fromProfileID = models.ForeignKey(Profile, models.DO_NOTHING, db_column='FromProfileID', related_name='connections_from')
    toProfileID = models.ForeignKey(Profile, models.DO_NOTHING, db_column='ToProfileID', related_name='connections_to')
    status = models.TextField(db_column='Status', choices=STATUS_CHOICES)
    createdDateTime = models.DateTimeField(db_column='CreatedDateTime', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Connection'
        unique_together = (('fromProfileID', 'toProfileID'),)
