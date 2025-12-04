"""
Firebase authentication middleware for Django.
"""

import firebase_admin
from firebase_admin import credentials, auth
from django.conf import settings
from django.http import JsonResponse
from .models import User


# Initialize Firebase Admin SDK
if settings.FIREBASE_CREDENTIALS_PATH:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)


class FirebaseAuthenticationMiddleware:
    """Middleware to authenticate requests using Firebase tokens."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Mark all API requests as CSRF exempt
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        # Skip authentication for admin, static files, and public endpoints
        skip_paths = [
            '/admin/',
            '/static/',
            '/api/users/register/',
        ]
        
        # Check if path should skip authentication
        for skip_path in skip_paths:
            if request.path.startswith(skip_path):
                return self.get_response(request)
        
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Missing or invalid authorization header'}, status=401)
        
        token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify Firebase token
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token['uid']
            
            # Get or create user
            try:
                user = User.objects.get(firebase_uid=firebase_uid)
                # Store user in a custom attribute that won't be overwritten
                request._firebase_user = user
                request.user = user
            except User.DoesNotExist:
                # User not found - they need to complete registration
                print(f"DEBUG: User with firebase_uid={firebase_uid} not found in database")
                return JsonResponse({'error': 'User profile not found. Please complete registration.'}, status=404)
            
            print(f"DEBUG: User authenticated: {user.email}, path: {request.path}")
            
        except Exception as e:
            print(f"DEBUG: Token verification failed: {str(e)}")
            return JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)
        
        response = self.get_response(request)
        print(f"DEBUG: Response status: {response.status_code}")
        return response

