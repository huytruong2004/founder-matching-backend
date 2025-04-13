from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.core.files.base import ContentFile
from django.http import HttpResponse
from .serializers import ProfileSerializer, ProfilePreviewCardSerializer, TagSerializer
from .models import Profile, UserAccount, ProfilePrivacySettings, Connection, Tags, ProfileTagInstances
from django.core.exceptions import ValidationError
from accounts.middlewares import JWTAuthenticationMiddleware
from discover.models import Matching
import json
import base64
import logging
import os
import tempfile
import mimetypes
from django.db.models import Q, Prefetch

logger = logging.getLogger(__name__)

class CreateProfileView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def validate_avatar_file(self, file):
        if not file:
            return None

        # Check file size (2MB = 2097152 bytes)
        if file.size > 2097152:
            raise ValidationError("Avatar file size must be less than 2MB")

        # Get file type from content type or filename
        content_type = file.content_type if hasattr(file, 'content_type') else None
        if content_type and content_type.startswith('image/'):
            file_type = content_type.split('/')[-1]
        else:
            file_type = os.path.splitext(file.name)[-1].lstrip('.')
        
        if file_type not in ['jpeg', 'jpg', 'png', 'gif']:
            raise ValidationError("Invalid file type. Allowed types: jpeg, jpg, png, gif")

        # Read and encode file data
        file_data = file.read()
        base64_data = base64.b64encode(file_data).decode('utf-8')
        return f'data:image/{file_type};base64,{base64_data}'

    @transaction.atomic
    def post(self, request):
        try:
            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                user_id = user_account.userID
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            profile_data = json.loads(request.data.get('ProfileInfo', '{}'))
            profile_data['userID'] = user_id

            logger.info(f"Received profile data: {profile_data}")
            logger.info(f"Tags in profile data: {profile_data.get('tags')}")

            # Handle avatar file
            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                try:
                    avatar_data = self.validate_avatar_file(avatar_file)
                    if avatar_data:
                        profile_data['avatar'] = avatar_data
                except ValidationError as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = ProfileSerializer(data=profile_data)
            if serializer.is_valid():
                profile = serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetUserProfilesView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]

    def get(self, request):
        try:
            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                user_id = user_account.userID
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get profiles with prefetched tags
            profiles = Profile.objects.filter(userID=user_id).prefetch_related(
                Prefetch(
                    'tags',
                    queryset=ProfileTagInstances.objects.select_related('tagID')
                )
            )

            if not profiles.exists():
                return Response(
                    {'error': 'No profiles found for this user'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            profile_data = []
            for profile in profiles:
                serializer = ProfilePreviewCardSerializer(profile)
                profile_data.append(serializer.data)

            return Response(profile_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetCurrentUserProfileView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        try:
            # Get profile ID from query params
            profile_id = request.query_params.get('profileId')
            if not profile_id:
                return Response(
                    {'error': 'Profile ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                user_id = user_account.userID
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get profile with prefetched tags and related data
            profile = Profile.objects.filter(
                profileID=profile_id,
                userID=user_id
            ).prefetch_related(
                Prefetch(
                    'tags',
                    queryset=ProfileTagInstances.objects.select_related('tagID')
                ),
                'experiences',
                'certificates',
                'achievements',
                'jobPositions'
            ).first()

            if not profile:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def patch(self, request):
        try:
            # Get profile ID from query params
            profile_id = request.query_params.get('profileId')
            if not profile_id:
                return Response(
                    {'error': 'Profile ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                user_id = user_account.userID
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get profile
            profile = Profile.objects.filter(
                profileID=profile_id,
                userID=user_id
            ).first()

            if not profile:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            profile_data = json.loads(request.data.get('ProfileInfo', '{}'))

            # Handle avatar file if present
            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                try:
                    avatar_data = self.validate_avatar_file(avatar_file)
                    if avatar_data:
                        profile_data['avatar'] = avatar_data
                except ValidationError as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = ProfileSerializer(profile, data=profile_data, partial=True)
            if serializer.is_valid():
                updated_profile = serializer.save()
                return Response(
                    {'message': 'Profile updated successfully'},
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetUserProfileByIdView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]

    def _check_connection_status(self, viewer_profileID, target_profileID):
        """Check if the viewer is connected to the target profile"""
        return Matching.objects.filter(
            (Q(candidateprofileid=viewer_profileID) & Q(startupprofileid=target_profileID)) |
            (Q(candidateprofileid=target_profileID) & Q(startupprofileid=viewer_profileID)),
            ismatched=True
        ).exists()

    def _filter_field_by_privacy(self, field_value, privacy_setting, is_connected):
        """Filter field based on privacy setting"""
        if privacy_setting == 'public':
            return field_value
        elif privacy_setting == 'connections' and is_connected:
            return field_value
        return None

    def get(self, request, profileID):
        try:
            # Get the authenticated user's account
            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                viewer_id = user_account.userID
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the target profile with prefetched data
            target_profile = Profile.objects.filter(
                profileID=profileID
            ).prefetch_related(
                'experiences',
                'certificates',
                'achievements',
                'jobPositions',
                'profileprivacysettings',
                Prefetch(
                    'tags',
                    queryset=ProfileTagInstances.objects.select_related('tagID')
                )
            ).first()

            if not target_profile:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if viewer is the profile owner
            is_owner = target_profile.userID_id == viewer_id

            # If not owner, check connection status
            is_connected = False
            if not is_owner:
                # Get viewer's active profile
                viewer_profile = Profile.objects.filter(userID=viewer_id).first()
                if not viewer_profile:
                    return Response(
                        {'error': 'Viewer profile not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                is_connected = self._check_connection_status(viewer_profile.profileID, profileID)

            # Serialize the profile
            serializer = ProfileSerializer(target_profile)
            profile_data = serializer.data

            # If viewer is owner, return full profile
            if is_owner:
                return Response(profile_data, status=status.HTTP_200_OK)

            # Get privacy settings
            privacy_settings = target_profile.profileprivacysettings

            # Filter fields based on privacy settings
            filtered_data = {
                'profileID': profile_data['profileID'],
                'isStartup': profile_data['isStartup'],
                'name': profile_data['name'],  # Name is always visible
                'avatar': profile_data['avatar'],  # Avatar is always visible
                'industry': self._filter_field_by_privacy(
                    profile_data['industry'],
                    privacy_settings.industryPrivacy,
                    is_connected
                ),
                'email': self._filter_field_by_privacy(
                    profile_data['email'],
                    privacy_settings.emailPrivacy,
                    is_connected
                ),
                'phoneNumber': self._filter_field_by_privacy(
                    profile_data['phoneNumber'],
                    privacy_settings.phoneNumberPrivacy,
                    is_connected
                ),
                'country': self._filter_field_by_privacy(
                    profile_data['country'],
                    privacy_settings.countryPrivacy,
                    is_connected
                ),
                'city': self._filter_field_by_privacy(
                    profile_data['city'],
                    privacy_settings.cityPrivacy,
                    is_connected
                ),
                'linkedInURL': self._filter_field_by_privacy(
                    profile_data['linkedInURL'],
                    privacy_settings.linkedInURLPrivacy,
                    is_connected
                ),
                'slogan': self._filter_field_by_privacy(
                    profile_data['slogan'],
                    privacy_settings.sloganPrivacy,
                    is_connected
                ),
                'websiteLink': profile_data['websiteLink'],  # Website link is always visible
                'description': profile_data['description'],  # Description is always visible
            }

            # Handle candidate-specific fields
            if not target_profile.isStartup:
                filtered_data.update({
                    'gender': self._filter_field_by_privacy(
                        profile_data['gender'],
                        privacy_settings.genderPrivacy,
                        is_connected
                    ),
                    'hobbyInterest': self._filter_field_by_privacy(
                        profile_data['hobbyInterest'],
                        privacy_settings.hobbyInterestPrivacy,
                        is_connected
                    ),
                    'education': self._filter_field_by_privacy(
                        profile_data['education'],
                        privacy_settings.educationPrivacy,
                        is_connected
                    ),
                    'dateOfBirth': self._filter_field_by_privacy(
                        profile_data['dateOfBirth'],
                        privacy_settings.dateOfBirthPrivacy,
                        is_connected
                    ),
                })

            # Handle startup-specific fields
            else:
                filtered_data.update({
                    'currentStage': profile_data['currentStage'],
                    'statement': profile_data['statement'],
                    'aboutUs': profile_data['aboutUs'],
                })

            # Handle related fields based on privacy
            if privacy_settings.achievementPrivacy == 'public' or \
               (privacy_settings.achievementPrivacy == 'connections' and is_connected):
                filtered_data['achievements'] = profile_data['achievements']
                filtered_data['experiences'] = profile_data['experiences']
                filtered_data['certificates'] = profile_data['certificates']

            # Job positions are always visible for startups
            if target_profile.isStartup:
                filtered_data['jobPositions'] = profile_data['jobPositions']

            # Tags are always visible
            filtered_data['tags'] = profile_data['tags']

            return Response(filtered_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateProfileView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def validate_avatar_file(self, file):
        if not file:
            return None

        # Check file size
        if file.size > 2097152:
            raise ValidationError("Avatar file size must be less than 2MB")

        # Get file type from content type or filename
        content_type = file.content_type if hasattr(file, 'content_type') else None
        if content_type and content_type.startswith('image/'):
            file_type = content_type.split('/')[-1]
        else:
            file_type = os.path.splitext(file.name)[-1].lstrip('.')
        
        if file_type not in ['jpeg', 'jpg', 'png', 'gif']:
            raise ValidationError("Invalid file type. Allowed types: jpeg, jpg, png, gif")

        # Read and encode file data
        file_data = file.read()
        base64_data = base64.b64encode(file_data).decode('utf-8')
        return f'data:image/{file_type};base64,{base64_data}'

    @transaction.atomic
    def patch(self, request):
        try:
            # Get profile ID from query params
            profile_id = request.query_params.get('profileId')
            if not profile_id:
                return Response(
                    {'error': 'Profile ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                user_id = user_account.userID
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                profile = Profile.objects.get(profileID=profile_id, userID=user_id)
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found or access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

            profile_data = json.loads(request.data.get('ProfileInfo', '{}'))
            profile_data['userID'] = user_id

            # Handle avatar file
            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                try:
                    avatar_data = self.validate_avatar_file(avatar_file)
                    if avatar_data:
                        profile_data['avatar'] = avatar_data
                except ValidationError as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = ProfileSerializer(profile, data=profile_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                    status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
