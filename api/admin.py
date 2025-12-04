"""
Admin configuration for PrepShark API.
"""

from django.contrib import admin
from .models import User, Question, MockTest, TestResult, UserProgress, Subscription, AdConfig, SubscriptionPlan, QuestionAttempt, DailyPracticePaper


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'exam_type', 'subscription_tier', 'created_at']
    list_filter = ['exam_type', 'subscription_tier']
    search_fields = ['email', 'name', 'firebase_uid']
    readonly_fields = ['firebase_uid', 'created_at', 'updated_at']


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'price', 'duration_days', 'is_active')
    search_fields = ('name', 'key')
    list_filter = ('is_active',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'subject', 'chapter', 'difficulty', 'is_premium', 'is_pyq']
    list_filter = ['subject', 'difficulty', 'is_premium', 'is_pyq']
    search_fields = ['question_text', 'question_id', 'chapter']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MockTest)
class MockTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam_type', 'total_questions', 'duration_minutes', 'is_premium']
    list_filter = ['exam_type', 'is_premium']
    search_fields = ['title', 'description']
    filter_horizontal = ['questions']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'test_type', 'score', 'total_questions', 'created_at']
    list_filter = ['test_type', 'created_at']
    search_fields = ['user__email', 'user__name']
    readonly_fields = ['created_at']


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'chapter', 'questions_attempted', 'accuracy']
    list_filter = ['subject']
    search_fields = ['user__email', 'chapter']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'started_at', 'expires_at']
    list_filter = ['plan', 'status']
    search_fields = ['user__email', 'payment_id']
    readonly_fields = ['started_at', 'created_at']


@admin.register(AdConfig)
class AdConfigAdmin(admin.ModelAdmin):
    list_display = ['ad_type', 'is_active', 'frequency']
    list_filter = ['ad_type', 'is_active']


@admin.register(DailyPracticePaper)
class DailyPracticePaperAdmin(admin.ModelAdmin):
    list_display = ['date', 'practice_type', 'created_at']
    list_filter = ['date', 'practice_type']
    filter_horizontal = ['questions']

