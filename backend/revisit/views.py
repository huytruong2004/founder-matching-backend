from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.paginator import Paginator
from accounts.middlewares import JWTAuthenticationMiddleware
from profiles.models import Profile
from profiles.serializers import ProfilePreviewCardSerializer
from .models import SavedProfiles, SkippedProfiles, ProfileViews
import logging

logger = logging.getLogger(__name__)

class GetViewedProfilesView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]

    def get(self, request):
        try:
            profile_id = request.query_params.get('profileID')
            if not profile_id:
                return Response(
                    {'error': 'profileID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                profile = Profile.objects.get(profileID=profile_id)
                if profile.userID.clerkUserID != request.user.username:
                    return Response(
                        {'error': 'You do not have permission to view these profiles'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            page = int(request.query_params.get('page', 1))
            per_page = 5

            viewed_profiles = ProfileViews.objects.filter(
                toProfileID=profile_id
            ).select_related(
                'fromProfileID'
            ).prefetch_related(
                'fromProfileID__tags'
            )

            paginator = Paginator(viewed_profiles, per_page)
            if page < 1 or page > paginator.num_pages:
                page = 1

            page_obj = paginator.get_page(page)
            
            serialized_profiles = []
            for viewed_profile in page_obj:
                profile_data = ProfilePreviewCardSerializer(viewed_profile.fromProfileID).data
                profile_data['occupation'] = profile_data.pop('industry')
                serialized_profiles.append(profile_data)

            response_data = {
                'total': paginator.count,
                'page': page,
                'perPage': per_page,
                'hasNext': page_obj.has_next(),
                'hasPrev': page_obj.has_previous(),
                'results': serialized_profiles
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': 'Invalid page number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in GetViewedProfilesView: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetSavedProfilesView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]
    
    def get(self, request):
        try:
            profile_id = request.query_params.get('profileID')
            if not profile_id:
                return Response(
                    {'error': 'profileID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                profile = Profile.objects.get(profileID=profile_id)
                if profile.userID.clerkUserID != request.user.username:
                    return Response(
                        {'error': 'You do not have permission to view these saved profiles'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            page = int(request.query_params.get('page', 1))
            per_page = 5

            saved_profiles = SavedProfiles.objects.filter(
                savedFromProfileID=profile_id
            ).select_related(
                'savedToProfileID'
            ).prefetch_related(
                'savedToProfileID__tags'
            )

            paginator = Paginator(saved_profiles, per_page)
            if page < 1 or page > paginator.num_pages:
                page = 1

            page_obj = paginator.get_page(page)
            
            serialized_profiles = []
            for saved_profile in page_obj:
                profile_data = ProfilePreviewCardSerializer(saved_profile.savedToProfileID).data
                profile_data['occupation'] = profile_data.pop('industry')
                serialized_profiles.append(profile_data)

            response_data = {
                'total': paginator.count,
                'page': page,
                'perPage': per_page,
                'hasNext': page_obj.has_next(),
                'hasPrev': page_obj.has_previous(),
                'results': serialized_profiles
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': 'Invalid page number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in GetSavedProfilesView: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetSkippedProfilesView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]

    def get(self, request):
        try:
            profile_id = request.query_params.get('profileID')
            if not profile_id:
                return Response(
                    {'error': 'profileID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                profile = Profile.objects.get(profileID=profile_id)
                if profile.userID.clerkUserID != request.user.username:
                    return Response(
                        {'error': 'You do not have permission to view these skipped profiles'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            page = int(request.query_params.get('page', 1))
            per_page = 5

            skipped_profiles = SkippedProfiles.objects.filter(
                skippedFromProfileID=profile_id
            ).select_related(
                'skippedToProfileID'
            ).prefetch_related(
                'skippedToProfileID__tags'
            )

            paginator = Paginator(skipped_profiles, per_page)
            if page < 1 or page > paginator.num_pages:
                page = 1

            page_obj = paginator.get_page(page)
            
            serialized_profiles = []
            for skipped_profile in page_obj:
                profile_data = ProfilePreviewCardSerializer(skipped_profile.skippedToProfileID).data
                profile_data['occupation'] = profile_data.pop('industry')
                serialized_profiles.append(profile_data)

            response_data = {
                'total': paginator.count,
                'page': page,
                'perPage': per_page,
                'hasNext': page_obj.has_next(),
                'hasPrev': page_obj.has_previous(),
                'results': serialized_profiles
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': 'Invalid page number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in GetSkippedProfilesView: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Create your views here.
