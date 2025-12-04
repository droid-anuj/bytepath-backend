"""
Custom DRF authentication class that uses the user set by Firebase middleware.
"""

from rest_framework import authentication


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    DRF authentication class that uses the user already set by Firebase middleware.
    """
    
    def authenticate(self, request):
        """
        Returns the user if it was set by the Firebase middleware.
        """
        # Access the underlying Django request, not the DRF wrapper
        django_request = request._request
        
        # Check for Firebase user stored by our middleware
        user = getattr(django_request, '_firebase_user', None)
        
        print(f"DEBUG AUTH: user type={type(user)}, has_id={hasattr(user, 'id') if user else False}")
        if user and hasattr(user, 'email'):
            print(f"DEBUG AUTH: user email={user.email}")
        
        # If middleware set a valid user, return it
        if user and hasattr(user, 'id'):
            return (user, None)
        
        # No authentication
        return None
