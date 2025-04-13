from rest_framework import serializers
from .models import (
    Profile, Experience, Certificate,
    Achievement, ProfilePrivacySettings, Countries,
    Tags, ProfileTagInstances, JobPosition, JobPositionTagInstances
)
from datetime import datetime
import re
import os
import base64
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['tagID', 'value', 'description']
        read_only_fields = ['tagID']

class ModelSerializer(serializers.ModelSerializer):
    """Base serializer that preserves the exact field names from the model"""
    def to_representation(self, instance):
        """Convert instance to JSON-serializable format"""
        ret = {}
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
                if attribute is not None:
                    ret[field.field_name] = field.to_representation(attribute)
                else:
                    ret[field.field_name] = None
            except Exception as e:
                ret[field.field_name] = None
        return ret

    def to_internal_value(self, data):
        return super().to_internal_value(data)

class ProfilePreviewCardSerializer(ModelSerializer):
    tags = serializers.SerializerMethodField()
    avatar = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['profileID', 'isStartup', 'name', 'industry', 'avatar', 'tags']

    def get_tags(self, obj):
        tag_instances = obj.tags.all()
        return [instance.tagID.value for instance in tag_instances]

    def validate_avatar(self, value):
        if value is None:
            return None
            
        # Check if it's already a base64 string
        if value.startswith('data:image/'):
            try:
                # Validate base64 format
                header, encoded = value.split(',', 1)
                if not header.startswith('data:image/'):
                    raise serializers.ValidationError("Invalid image format")
                
                # Try decoding to validate base64
                try:
                    base64.b64decode(encoded)
                except Exception:
                    raise serializers.ValidationError("Invalid base64 encoding")
                return value
            except ValueError:
                raise serializers.ValidationError("Invalid image format")
        return value

class ExperienceSerializer(ModelSerializer):
    startDate = serializers.DateField(format='%Y-%m-%d')
    endDate = serializers.DateField(required=False, allow_null=True, format='%Y-%m-%d')
    
    class Meta:
        model = Experience
        fields = [
            'companyName', 'role', 'location',
            'description', 'startDate', 'endDate'
        ]
        extra_kwargs = {
            'startDate': {'required': True},
            'endDate': {'required': False},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.startDate:
            data['startDate'] = instance.startDate.strftime('%Y-%m-%d')
        if instance.endDate:
            data['endDate'] = instance.endDate.strftime('%Y-%m-%d')
        return data

class CertificateSerializer(ModelSerializer):
    startDate = serializers.DateField(required=False, allow_null=True, format='%Y-%m-%d')
    endDate = serializers.DateField(required=False, allow_null=True, format='%Y-%m-%d')
    
    class Meta:
        model = Certificate
        fields = [
            'name', 'skill', 'description',
            'startDate', 'endDate', 'gpa'
        ]
        extra_kwargs = {
            'name': {'required': True},
            'skill': {'required': True},
        }

class AchievementSerializer(ModelSerializer):
    date = serializers.DateField(required=False, allow_null=True, format='%Y-%m-%d')
    
    class Meta:
        model = Achievement
        fields = ['name', 'description', 'date']
        extra_kwargs = {
            'name': {'required': True},
        }

class JobPositionSerializer(ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    startDate = serializers.DateField(required=False, allow_null=True, format='%Y-%m-%d')
    
    class Meta:
        model = JobPosition
        fields = [
            'jobTitle', 'isOpening', 'country', 'city',
            'startDate', 'description', 'tags'
        ]
        extra_kwargs = {
            'jobTitle': {'required': True},
            'country': {'required': True},
        }

class ProfilePrivacySettingsSerializer(ModelSerializer):
    class Meta:
        model = ProfilePrivacySettings
        exclude = ['profileID']
        extra_kwargs = {
            'industryPrivacy': {'required': True},
            'emailPrivacy': {'required': True},
            'phoneNumberPrivacy': {'required': True},
            'countryPrivacy': {'required': True},
            'cityPrivacy': {'required': True},
            'linkedInURLPrivacy': {'required': True},
            'sloganPrivacy': {'required': True},
            'achievementPrivacy': {'required': True},
        }

class ProfileSerializer(ModelSerializer):
    experiences = ExperienceSerializer(many=True, required=False)
    certificates = CertificateSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    jobPositions = JobPositionSerializer(many=True, required=False)
    privacySettings = ProfilePrivacySettingsSerializer(source='profileprivacysettings', required=False)
    dateOfBirth = serializers.DateField(required=False, allow_null=True, format='%Y-%m-%d')
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    avatar = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = [
            'profileID', 'userID', 'isStartup', 'name', 'email',
            'industry', 'phoneNumber', 'country', 'city',
            'linkedInURL', 'slogan', 'websiteLink',
            'avatar', 'description', 'hobbyInterest',
            'gender', 'education', 'dateOfBirth',
            'currentStage', 'statement', 'aboutUs',
            'experiences', 'certificates', 'achievements',
            'jobPositions', 'privacySettings', 'tags'
        ]
        extra_kwargs = {
            'profileID': {'read_only': True}
        }

    def get_tags(self, obj):
        try:
            tag_instances = obj.tags.all()
            return [instance.tagID.value for instance in tag_instances]
        except Exception as e:
            logger.error(f"Error getting tags: {str(e)}")
            return []

    def to_representation(self, instance):
        """Convert instance to JSON-serializable format"""
        try:
            data = super().to_representation(instance)
            
            # Handle date fields
            if instance.dateOfBirth:
                data['dateOfBirth'] = instance.dateOfBirth.strftime('%Y-%m-%d')

            # Handle related fields
            data['experiences'] = ExperienceSerializer(instance.experiences.all(), many=True).data
            data['certificates'] = CertificateSerializer(instance.certificates.all(), many=True).data
            data['achievements'] = AchievementSerializer(instance.achievements.all(), many=True).data
            data['jobPositions'] = JobPositionSerializer(instance.jobPositions.all(), many=True).data
            
            # Handle tags
            data['tags'] = self.get_tags(instance)
            
            return data
        except Exception as e:
            logger.error(f"Error in to_representation: {str(e)}")
            raise

    def validate_avatar(self, value):
        if value is None:
            return None
            
        # Check if it's already a base64 string
        if value.startswith('data:image/'):
            try:
                # Validate base64 format
                header, encoded = value.split(',', 1)
                if not header.startswith('data:image/'):
                    raise serializers.ValidationError("Invalid image format")
                
                try:
                    base64.b64decode(encoded)
                except Exception:
                    raise serializers.ValidationError("Invalid base64 encoding")
                    
                return value
            except Exception as e:
                raise serializers.ValidationError(f"Invalid avatar format: {str(e)}")
                
        raise serializers.ValidationError("Avatar must be a base64 encoded image string")

    @transaction.atomic
    def _process_tags(self, profile, tags_data):
        if tags_data is None:
            logger.info("No tags data provided")
            return

        logger.info(f"Processing tags for profile {profile.profileID}: {tags_data}")

        # Get existing tag values for the profile
        existing_tag_values = set(
            ProfileTagInstances.objects.filter(profileOwnerID=profile)
            .select_related('tagID')
            .values_list('tagID__value', flat=True)
        )
        logger.info(f"Existing tag values: {existing_tag_values}")

        # Convert new tags to set for comparison
        new_tag_values = set(tags_data)
        logger.info(f"New tag values: {new_tag_values}")

        # Find tags to remove (exist in DB but not in new data)
        tags_to_remove = existing_tag_values - new_tag_values
        if tags_to_remove:
            logger.info(f"Removing tags: {tags_to_remove}")
            ProfileTagInstances.objects.filter(
                profileOwnerID=profile,
                tagID__value__in=tags_to_remove
            ).delete()

        # Find tags to add (exist in new data but not in DB)
        tags_to_add = new_tag_values - existing_tag_values
        if tags_to_add:
            logger.info(f"Adding tags: {tags_to_add}")
            # Get or create tags and build instances for bulk create
            new_instances = []
            for tag_value in tags_to_add:
                tag, created = Tags.objects.get_or_create(
                    value=tag_value,
                    defaults={'description': ''}
                )
                logger.info(f"{'Created' if created else 'Found'} tag: {tag_value}")
                new_instances.append(
                    ProfileTagInstances(
                        profileOwnerID=profile,
                        tagID=tag
                    )
                )
            
            # Bulk create new tag instances
            if new_instances:
                ProfileTagInstances.objects.bulk_create(new_instances)
                logger.info(f"Created {len(new_instances)} new tag instances")

    @transaction.atomic
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', None)
        experiences_data = validated_data.pop('experiences', [])
        certificates_data = validated_data.pop('certificates', [])
        achievements_data = validated_data.pop('achievements', [])
        job_positions_data = validated_data.pop('jobPositions', [])
        privacy_settings_data = validated_data.pop('profileprivacysettings', None)

        profile = Profile.objects.create(**validated_data)

        # Process tags
        self._process_tags(profile, tags_data)

        new_job_positions = []
        new_job_position_tags = []
        
        for job_data in job_positions_data:
            job_tags = job_data.pop('tags', [])
            job = JobPosition(profileOwner=profile, **job_data)
            new_job_positions.append(job)
            
            for tag_value in job_tags:
                tag, _ = Tags.objects.get_or_create(
                    value=tag_value,
                    defaults={'description': ''}
                )
                new_job_position_tags.append(
                    JobPositionTagInstances(
                        jobPositionID=job,
                        tagID=tag
                    )
                )

        created_jobs = JobPosition.objects.bulk_create(new_job_positions)
    
        if new_job_position_tags:
            for i, job in enumerate(created_jobs):
                for tag in new_job_position_tags:
                    if tag.jobPositionID == new_job_positions[i]:
                        tag.jobPositionID = job
            JobPositionTagInstances.objects.bulk_create(new_job_position_tags)

        # Create experiences
        if experiences_data:
            Experience.objects.bulk_create([
                Experience(profileOwner=profile, **exp_data)
                for exp_data in experiences_data
            ])

        # Create certificates
        if certificates_data:
            Certificate.objects.bulk_create([
                Certificate(profileOwner=profile, **cert_data)
                for cert_data in certificates_data
            ])

        # Create achievements
        if achievements_data:
            Achievement.objects.bulk_create([
                Achievement(profileOwner=profile, **ach_data)
                for ach_data in achievements_data
            ])

        # Create privacy settings
        if privacy_settings_data:
            ProfilePrivacySettings.objects.create(
                profileID=profile,
                **privacy_settings_data
            )
        else:
            # Create default privacy settings
            default_settings = self.get_default_privacy_settings()
            ProfilePrivacySettings.objects.create(
                profileID=profile,
                **default_settings
            )

        return profile

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        experiences_data = validated_data.pop('experiences', []) if 'experiences' in validated_data else None
        certificates_data = validated_data.pop('certificates', []) if 'certificates' in validated_data else None
        achievements_data = validated_data.pop('achievements', []) if 'achievements' in validated_data else None
        job_positions_data = validated_data.pop('jobPositions', []) if 'jobPositions' in validated_data else None
        privacy_settings_data = validated_data.pop('profileprivacysettings', None)

        for attr, value in validated_data.items():
            if not attr.endswith('_set'):
                setattr(instance, attr, value)
        instance.save(update_fields=[field for field in validated_data.keys() if not field.endswith('_set')])

        # Update tags if provided
        if tags_data is not None:
            self._process_tags(instance, tags_data)

        # Update experiences if provided
        if experiences_data is not None:
            instance.experiences.all().delete()
            Experience.objects.bulk_create([
                Experience(profileOwner=instance, **exp_data)
                for exp_data in experiences_data
            ])

        # Update certificates if provided
        if certificates_data is not None:
            instance.certificates.all().delete()
            Certificate.objects.bulk_create([
                Certificate(profileOwner=instance, **cert_data)
                for cert_data in certificates_data
            ])

        # Update achievements if provided
        if achievements_data is not None:
            instance.achievements.all().delete()
            Achievement.objects.bulk_create([
                Achievement(profileOwner=instance, **ach_data)
                for ach_data in achievements_data
            ])

        # Update job positions if provided
        if job_positions_data is not None:
            # Delete existing job positions and their tags
            job_positions = instance.jobPositions.all()
            JobPositionTagInstances.objects.filter(jobPositionID__in=job_positions).delete()
            job_positions.delete()

            # Create new job positions and their tags
            new_job_positions = []
            new_job_position_tags = []
            
            for job_data in job_positions_data:
                job_tags = job_data.pop('tags', [])
                job = JobPosition(profileOwner=instance, **job_data)
                new_job_positions.append(job)
                
                for tag_value in job_tags:
                    tag, _ = Tags.objects.get_or_create(
                        value=tag_value,
                        defaults={'description': ''}
                    )
                    new_job_position_tags.append(
                        JobPositionTagInstances(
                            jobPositionID=job,
                            tagID=tag
                        )
                    )

            created_jobs = JobPosition.objects.bulk_create(new_job_positions)
            
            if new_job_position_tags:
                for i, job in enumerate(created_jobs):
                    for tag in new_job_position_tags:
                        if tag.jobPositionID == new_job_positions[i]:
                            tag.jobPositionID = job
                JobPositionTagInstances.objects.bulk_create(new_job_position_tags)

        # Update privacy settings if provided
        if privacy_settings_data is not None:
            privacy_settings = instance.profileprivacysettings
            for field, value in privacy_settings_data.items():
                setattr(privacy_settings, field, value)
            privacy_settings.save(update_fields=list(privacy_settings_data.keys()) if privacy_settings_data else None)

        # Refresh from database to get updated data
        instance.refresh_from_db()
        return instance

    def get_default_privacy_settings(self):
        return {
            'genderPrivacy': 'public',
            'industryPrivacy': 'public',
            'emailPrivacy': 'public',
            'phoneNumberPrivacy': 'public',
            'countryPrivacy': 'public',
            'cityPrivacy': 'public',
            'universityPrivacy': 'public',
            'linkedInURLPrivacy': 'public',
            'sloganPrivacy': 'public',
            'websiteLinkPrivacy': 'public',
            'certificatePrivacy': 'public',
            'experiencePrivacy': 'public',
            'hobbyInterestPrivacy': 'public',
            'educationPrivacy': 'public',
            'dateOfBirthPrivacy': 'public',
            'achievementPrivacy': 'public'
        }

    def validate_dateOfBirth(self, value):
        if value is None:
            return None

        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid date format. Please use YYYY-MM-DD"
                )
        return value

    def validate(self, data):
        if data.get('isStartup'):
            if not data.get('currentStage'):
                raise serializers.ValidationError(
                    "currentStage is required for startup profiles"
                )
        
        if country := data.get('country'):
            if not Countries.objects.filter(en_short_name=country).exists():
                raise serializers.ValidationError({
                    'country': f'Country "{country}" is not valid. Please select a country from the provided list.'
                })
        
        return data