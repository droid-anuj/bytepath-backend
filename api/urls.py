"""
URL configuration for API app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, QuestionViewSet, MockTestViewSet, TestResultViewSet,
    UserProgressViewSet, SubscriptionViewSet, SubscriptionPlanViewSet, AdConfigViewSet,
    DailyPracticeViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'mock-tests', MockTestViewSet)
router.register(r'tests', TestResultViewSet)
router.register(r'progress', UserProgressViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'plans', SubscriptionPlanViewSet)
router.register(r'daily-practice', DailyPracticeViewSet, basename='daily-practice')
router.register(r'ads', AdConfigViewSet, basename='ad')

urlpatterns = [
    path('', include(router.urls)),
]
