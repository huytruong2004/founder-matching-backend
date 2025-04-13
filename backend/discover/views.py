from datetime import datetime
from multiprocessing.managers import BaseManager
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction
from django.core.files.base import ContentFile
from django.http import HttpResponse
from .serializers import ProfileSerializer, ProfilePreviewCardSerializer, TagSerializer
from .models import Profile, UserAccount, ProfilePrivacySettings, Tags, ProfileTagInstances, Matching, ProfileViews
from django.core.exceptions import ValidationError
from accounts.middlewares import JWTAuthenticationMiddleware
import json
import base64
import logging
import os
import tempfile
import mimetypes
from django.db.models import Q, Prefetch
from typing import Optional

logger = logging.getLogger(__name__)

# Create your views here.
class GetConnectionsView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]

    def get(self, request):

        print(request)

        try:
            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                user_id = user_account.userID
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            profile_id = request.query_params.get('profileID')
            if not profile_id:
                return Response(
                    {'error': 'profileID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                profile_id = int(profile_id)
            except ValueError:
                return Response(
                    {'error': 'profileID must be an integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            

            # Get profiles owned by this user with prefetched tags
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

            # Check if profile_id is in the list of profiles owned by this user
            current_profile : Profile = None
            for profile in profiles:
                print(profile.profileID, profile.name)
                if profile.profileID == profile_id:
                    current_profile = profile
                    break
            else:
                return Response(
                    {'error': 'Profile not found or access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if current_profile.isStartup:
                # Get the list of connected profiles in the Matching table satisfying:
                # startupprofileid = current_profile.profileID
                connected_profile_ids = Matching.objects.filter(
                    startupprofileid=current_profile.profileID,
                    ismatched=True
                )
                # Get the array of candidates profiles only:
                connected_profile_ids = [profile.candidateprofileid_id for profile in connected_profile_ids]
            else:
                # Get the list of connected profiles in the Matching table satisfying:
                # candidateprofileid = current_profile.profileID
                connected_profile_ids = Matching.objects.filter(
                    candidateprofileid=current_profile.profileID,
                    ismatched=True
                )
                # Get the array of startupprofiles only:
                connected_profile_ids = [profile.startupprofileid_id for profile in connected_profile_ids]

            # Debug: print all connected profiles id 
            print ("Connected profiles:")
            for profile in connected_profile_ids:
                print(profile)

            # Get the page number (page) and page size (perPage) from the request
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('perPage', 5))

            # Calculate the index range according to the page and per_page
            start_index = (page - 1) * per_page
            end_index = start_index + per_page

            print(start_index, end_index)

            # Get the profiles from the list of ids given by connected_profile_ids
            profiles = Profile.objects.filter(profileID__in=connected_profile_ids[start_index:end_index]).prefetch_related(
                Prefetch(
                    'tags',
                    queryset=ProfileTagInstances.objects.select_related('tagID')
                )
            )

            # Serialize the profiles            
            serialized_profiles_data = []
            for profile in profiles:
                serializer = ProfilePreviewCardSerializer(profile)
                serialized_profiles_data.append(serializer.data)

            response_data = {
                'total': len(connected_profile_ids),
                'page': page,
                'perPage': per_page,
                'hasNext': end_index < len(connected_profile_ids),
                'hasPrev': page > 1,
                'results': serialized_profiles_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DiscoverView(APIView):
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

            profile_id = request.query_params.get('profileID')
            if not profile_id:
                return Response(
                    {'error': 'profileID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('perPage', 20))

            # Verify profile belongs to user
            try:
                requesting_profile = Profile.objects.get(profileID=profile_id)
                if requesting_profile.userID_id != user_id:
                    return Response(
                        {'error': 'Profile does not belong to authenticated user'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'Profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            connected_profile_ids = Matching.objects.filter(
                Q(candidateprofileid=profile_id, candidatestatus='accepted') |
                Q(startupprofileid=profile_id, startupstatus='accepted')
            ).values_list('candidateprofileid', 'startupprofileid')
            
            connected_ids = set()
            for candidate_id, startup_id in connected_profile_ids:
                connected_ids.add(candidate_id)
                connected_ids.add(startup_id)

            # Get rejected profile IDs
            rejected_profile_ids = Matching.objects.filter(
                Q(candidateprofileid=profile_id, candidatestatus='rejected') |
                Q(startupprofileid=profile_id, startupstatus='rejected')
            ).values_list(
                'candidateprofileid' if requesting_profile.isStartup else 'startupprofileid',
                flat=True
            )

            # Get profiles to exclude (own profiles, connected, and rejected)
            exclude_profiles = set(list(connected_ids) + list(rejected_profile_ids))
            exclude_profiles.add(int(profile_id))  # Add requesting profile ID
            user_profile_ids = Profile.objects.filter(userID=user_id).values_list('profileID', flat=True)
            exclude_profiles.update(user_profile_ids)
            print("Connected profiles:", connected_ids)
            print("Rejected profiles:", rejected_profile_ids)
            print("User profiles:", user_profile_ids)
            print("=> Excluded profiles:", exclude_profiles)

            # Query for discoverable profiles
            all_discoverable_profiles = Profile.objects.exclude(
                profileID__in=exclude_profiles
            ).prefetch_related(
                'experiences',
                'certificates',
                'achievements',
                'profileprivacysettings'
            ).order_by('profileID')  # Add consistent ordering

            # Calculate total count and pagination
            total_count = all_discoverable_profiles.count()
            start_index = (page - 1) * per_page
            end_index = start_index + per_page

            # Get the paginated profiles
            discoverable_profiles = all_discoverable_profiles[start_index:end_index]

            # Serialize the profiles
            serializer = ProfileSerializer(discoverable_profiles, many=True)

            # Prepare paginated response
            response_data = {
                'total': total_count,
                'page': page,
                'perPage': per_page,
                'hasNext': end_index < total_count,
                'hasPrev': page > 1,
                'results': serializer.data
            }

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in discover view: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConnectView(APIView):
    def post(self, request):
        """
        /connect/:
    post:
      tags:
        - Connections
      summary: Establish a connection between two profiles
      description: Request to connect profilefromId to profile to_id.
      operationId: connectRequest
      parameters:
        - name: fromID
          in: query
          required: true
          schema:
            type: integer
            format: int32
            minimum: 0
            maximum: 2147483647
            example: 11
        - name: toID
          in: query
          required: true
          schema:
            type: integer
            format: int32
            minimum: 0
            maximum: 2147483647
            example: 7
      responses:
        '200':
          description: Connection request sent successfully.
          content:
            application/json:
              schema:
                type: object
                additionalProperties: false
                properties:
                  message:
                    type: string
                    example: "Connection request sent successfully."
                    maxLength: 255
                    pattern: "^([[:print:]])*$"
        '404':
          description: Profile not found
          content:
            application/json:
              schema:
                type: object
                additionalProperties: false
                properties:
                  error:
                    type: string
                    example: "Profile to connect to is not found."
                    maxLength: 255
                    pattern: "^([[:print:]])*$"
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                type: object
                additionalProperties: false
                properties:
                  error:
                    type: string
                    example: "Unauthorized access: Not logged-in or invalid token."
                    maxLength: 255
                    pattern: "^([[:print:]])*$"
        '403':
          description: Forbidden
          content:
            application/json:
              schema:
                type: object
                additionalProperties: false
                properties:
                  error:
                    type: string
                    example: "Forbidden access: User does not own this profile, therefore cannot request a connection from this profile."
                    maxLength: 255
                    pattern: "^([[:print:]])*$"
        default:
          description: Unexpected error
          content:
            application/json:
              schema:
                type: object
                additionalProperties: false
                properties:
                  error:
                    type: string
                    example: "An unexpected error occurred"
                    maxLength: 255
                    pattern: "^([[:print:]])*$"
        """
        try:
            from_id = request.query_params.get('fromID')
            to_id = request.query_params.get('toID')

            if not from_id or not to_id:
                return Response(
                    {'error': 'Profile IDs are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            from_id = int(from_id)
            to_id = int(to_id)

            if not from_id or not to_id or from_id == to_id:
                return Response(
                    {'error': 'Invalid profile IDs'},
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

            
            # Get profiles owned by this user with prefetched tags
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

            # Check if profile_id is in the list of profiles owned by this user
            current_profile : Profile = None
            for profile in profiles:
                if profile.profileID == from_id:
                    current_profile = profile
                    is_startup = current_profile.isStartup
                    break
            else:
                return Response(
                    {'error': 'Profile not found or access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if is_startup:
                startup_id = from_id
                candidate_id = to_id
            else:
                startup_id = to_id
                candidate_id = from_id

            # Check if toID exists in the profile table
            to_profile = Profile.objects.filter(profileID=to_id).first()
            if not to_profile:
                return Response(
                    {'error': 'Profile to connect to is not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            currentdatetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("Current datetime: %s" % currentdatetime)

            # Check the connection status startup_id -> candidate_id in the Matching table
            matching = Matching.objects.filter(candidateprofileid_id=candidate_id, startupprofileid_id=startup_id).first()
            if matching:
                if matching.ismatched:
                    return Response(
                        {'error': 'Connection request is denied: Already connected.'},
                        status=status.HTTP_409_CONFLICT
                    )
                else:
                    if is_startup:
                        if matching.candidatestatus == 'accepted':
                            matching.candidatestatus = 'accepted'
                            matching.startupstatus = 'accepted'
                            matching.ismatched = True
                            matching.matchdate = currentdatetime
                            matching.save()
                            return Response(
                                {'message': 'Connection request sent successfully. You are now connected with this profile.'},
                                status=status.HTTP_200_OK
                            )
                        elif matching.candidatestatus == 'rejected':
                            return Response(
                                {'error': 'Connection request is denied: Candidate rejected your request.'},
                                status=status.HTTP_409_CONFLICT
                            )
                        elif matching.candidatestatus == 'pending':
                            return Response(
                                {'error': 'Connection request is denied: Pending acceptance from recipient.'},
                                status=status.HTTP_409_CONFLICT
                            )
                        else:
                            return Response(
                                {'error': 'Bad database value for candidatestatus: %s' % matching.candidatestatus},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
                    else:
                        if matching.startupstatus == 'accepted':
                            matching.candidatestatus = 'accepted'
                            matching.startupstatus = 'accepted'
                            matching.ismatched = True
                            matching.matchdate = currentdatetime
                            matching.save()
                            return Response(
                                {'message': 'Connection request sent successfully. You are now connected with this profile.'},
                                status=status.HTTP_200_OK
                            )
                        elif matching.startupstatus == 'rejected':
                            return Response(
                                {'error': 'Connection request is denied: Startup rejected your request.'},
                                status=status.HTTP_409_CONFLICT
                            )
                        elif matching.startupstatus == 'pending':
                            return Response(
                                {'error': 'Connection request is denied: Pending acceptance from recipient.'},
                                status=status.HTTP_409_CONFLICT
                            )
                        else:
                            return Response(
                                {'error': 'Bad database value for startupstatus: %s' % matching.startupstatus},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
            else:
                if is_startup:
                    matching = Matching(candidateprofileid_id=candidate_id, startupprofileid_id=startup_id, candidatestatus='pending', startupstatus='accepted')
                else:
                    matching = Matching(candidateprofileid_id=candidate_id, startupprofileid_id=startup_id, candidatestatus='accepted', startupstatus='pending')
                matching.ismatched = False
                matching.matchdate = currentdatetime
                matching.save()
                return Response(
                    {'message': 'Connection request sent successfully. Waiting for approval.'},
                    status=status.HTTP_200_OK
                )
            
        except Exception as e:
            logger.error(f"Error in discover view: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CountViewView(APIView):
    authentication_classes = [JWTAuthenticationMiddleware]

    def post(self, request):
        try:
            # Get authenticated user
            try:
                user_account = UserAccount.objects.get(clerkUserID=request.user.username)
            except UserAccount.DoesNotExist:
                return Response(
                    {'error': 'User account not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get and validate parameters
            from_id = request.query_params.get('fromID')
            to_id = request.query_params.get('toID')

            if not from_id or not to_id:
                return Response(
                    {'error': 'Both fromID and toID are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate profiles exist
            try:
                from_profile = Profile.objects.get(profileID=from_id)
                to_profile = Profile.objects.get(profileID=to_id)
            except Profile.DoesNotExist:
                return Response(
                    {'error': 'One or both profiles not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Verify user owns the from_profile
            if from_profile.userID_id != user_account.userID:
                return Response(
                    {'error': 'User does not own the fromID profile'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Create view record
            ProfileViews.objects.create(
                fromProfileID=from_profile,
                toProfileID=to_profile
            )

            return Response(
                {'message': 'View count updated'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error in CountViewView: {str(e)}")
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )