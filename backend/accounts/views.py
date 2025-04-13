from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import UserAccount
from .serializers import UserAccountSerializer

class UserAccountViewSet(viewsets.ModelViewSet):
    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return the user account for the currently authenticated user
        """
        user = self.request.user
        return UserAccount.objects.filter(clerkUserID=user.username)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Get the current user's account information
    """
    try:
        user_account = UserAccount.objects.get(clerkUserID=request.user.username)
        serializer = UserAccountSerializer(user_account)
        return Response(serializer.data)
    except UserAccount.DoesNotExist:
        return Response({"error": "User account not found"}, status=404)
