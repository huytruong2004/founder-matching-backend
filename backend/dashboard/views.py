from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import DashboardView, ViewHistory, ProfilePreviewCard
from .serializers import DashboardViewSerializer
from profiles.models import Profile, UserAccount
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            profile_id = request.query_params.get('profileID')
            logger.info(f"Received request for profile_id: {profile_id}")
            
            if not profile_id:
                return Response({"error": "profileID is required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                logger.info(f"Attempting to fetch profile with ID: {profile_id}")
                
                try:
                    user_account = UserAccount.objects.get(clerkUserID=request.user.username)
                    logger.debug(f"Found UserAccount with ID: {user_account.userID}")
                except UserAccount.DoesNotExist:
                    logger.error(f"No UserAccount found for clerk ID: {request.user.username}")
                    return Response(
                        {"error": "User account not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                profile = Profile.objects.get(profileID=profile_id)
                if profile.userID.userID != user_account.userID:
                    return Response({"error": "You don't have access to this profile"}, status=status.HTTP_403_FORBIDDEN)
                
            except Profile.DoesNotExist:
                logger.warning(f"Profile not found for ID: {profile_id}")
                return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error accessing profile: {str(e)}")
                return Response({"error": f"Error accessing profile: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                # Get view count
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM "ProfileViews" 
                        WHERE "ToProfileID" = %s
                    """, [profile_id])
                    viewed_count = cursor.fetchone()[0]
                    logger.debug(f"View count for profile {profile_id}: {viewed_count}")

                # Get view history for last 30 days
                thirty_days_ago = timezone.now() - timedelta(days=30)
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            to_char("ViewedAt"::date, 'YYYY-MM-DD') as day,
                            COUNT(*) as count
                        FROM "ProfileViews"
                        WHERE "ToProfileID" = %s
                        AND "ViewedAt" >= %s
                        GROUP BY "ViewedAt"::date
                        ORDER BY "ViewedAt"::date DESC
                    """, [profile_id, thirty_days_ago])
                    viewed_history = [
                        ViewHistory(time=row[0], count=row[1])
                        for row in cursor.fetchall()
                    ]
                    logger.debug(f"Retrieved {len(viewed_history)} days of view history within last 30 days")

                # Get connect request count
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM "Matching" 
                        WHERE ("CandidateProfileID" = %s OR "StartupProfileID" = %s)
                        AND ("CandidateStatus" = 'pending' OR "StartupStatus" = 'pending')
                    """, [profile_id, profile_id])
                    connect_request_count = cursor.fetchone()[0]
                    logger.debug(f"Connect request count: {connect_request_count}")

                # Get matched profiles count
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM "Matching" 
                        WHERE ("CandidateProfileID" = %s OR "StartupProfileID" = %s)
                        AND "IsMatched" = true
                    """, [profile_id, profile_id])
                    matched_profiles_count = cursor.fetchone()[0]
                    logger.info(f"Profile ID: {profile_id}, Raw matched profiles count from DB: {matched_profiles_count}")
                    logger.debug(f"Matched profiles count: {matched_profiles_count}")

                # Get sample profiles (4 most recent viewers)
                with connection.cursor() as cursor:
                    cursor.execute("""
                        WITH RankedViews AS (
                            SELECT DISTINCT ON (pv."FromProfileID") 
                                pv."FromProfileID",
                                pv."ViewedAt",
                                p."ProfileID",
                                p."IsStartup",
                                p."Name",
                                p."Industry" as occupation,
                                p."Avatar"
                            FROM "ProfileViews" pv
                            JOIN "Profile" p ON p."ProfileID" = pv."FromProfileID"
                            WHERE pv."ToProfileID" = %s
                            ORDER BY pv."FromProfileID", pv."ViewedAt" DESC
                        )
                        SELECT 
                            rv."ProfileID",
                            rv."IsStartup",
                            rv."Name",
                            rv.occupation,
                            rv."Avatar",
                            ARRAY_AGG(DISTINCT t."Value") FILTER (WHERE t."Value" IS NOT NULL) as tags
                        FROM RankedViews rv
                        LEFT JOIN "ProfileTagInstances" pti ON pti."ProfileOwnerID" = rv."ProfileID"
                        LEFT JOIN "Tags" t ON t."ID" = pti."TagID"
                        GROUP BY 
                            rv."ProfileID",
                            rv."IsStartup",
                            rv."Name",
                            rv.occupation,
                            rv."Avatar",
                            rv."ViewedAt"
                        ORDER BY rv."ViewedAt" DESC
                        LIMIT 4
                    """, [profile_id])
                    
                    sample_profiles = []
                    for row in cursor.fetchall():
                        sample_profiles.append(ProfilePreviewCard(
                            profileID=row[0],
                            isStartup=row[1],
                            name=row[2],
                            occupation=row[3],
                            avatar=row[4],
                            tags=row[5] if row[5] else []
                        ))
                    logger.debug(f"Retrieved {len(sample_profiles)} sample profiles")

            except Exception as db_error:
                logger.error(f"Database error: {str(db_error)}")
                return Response(
                    {"error": f"Database error: {str(db_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            try:
                # Create dashboard view object
                dashboard = DashboardView(
                    viewedCount=viewed_count,
                    connectRequestCount=connect_request_count,
                    matchedProfilesCount=matched_profiles_count
                )

                # Since these are M2M fields and we're using unmanaged models,
                # we'll create a temporary structure for serialization
                dashboard_data = {
                    'viewedCount': viewed_count,
                    'viewedHistory': viewed_history,
                    'connectRequestCount': connect_request_count,
                    'matchedProfilesCount': matched_profiles_count,
                    'sampleProfiles': sample_profiles
                }

                serializer = DashboardViewSerializer(dashboard_data)
                return Response(serializer.data)

            except Exception as serializer_error:
                logger.error(f"Serialization error: {str(serializer_error)}")
                return Response(
                    {"error": f"Serialization error: {str(serializer_error)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
