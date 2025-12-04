import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.routers import DefaultRouter
from api.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

print("Registered URLs:")
for pattern in router.urls:
    print(f"  {pattern.pattern}")
