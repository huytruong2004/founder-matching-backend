from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def test_api_view(request):
    if request.method == 'POST':
        try:
            print("Raw request body:", request.body)
            # Parse the JSON body
            data = json.loads(request.body)
            print("Parsed data:", data)  
            # Extract 'name' and 'email' from the request
            name = data.get('name', 'Anonymous')  # Default to 'Anonymous' if 'name' is not provided
            email = data.get('email', 'No Email Provided')  # Default if 'email' is missing
            jwt = data.get('jwt', 'No JWT Provided')

            # Return a custom message including name and email
            return JsonResponse({
                "message": f"Hello, {name}! Your email is {email}. Your JWT is {jwt}.",
                "status": "success",
            })
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON", "status": "error"},
                status=400
            )

    # Default GET response
    return JsonResponse({"message": "Hello from Django!", "status": "success"})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ProtectedDashboardView(APIView):
    permission_classes = [IsAuthenticated]  # Requires token validation

    def post(self, request):
        user = request.user  # This is set by the middleware
        return Response({
            "message": "Token is valid!",
            "user_email": user.email,
            "user_id": user.id,
            "username": user.username,
            "user_first_name": request.user.first_name,
            "user_last_name": request.user.last_name,
        })
    
    def get(self, request):
        return Response({
            "message": "GET method is allowed",
            "username": request.user.username,
        })