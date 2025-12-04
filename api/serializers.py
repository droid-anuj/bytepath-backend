"""
Serializers for PrepShark API.
"""

from rest_framework import serializers
from .models import User, Subscription, Question, MockTest, TestResult, UserProgress, AdConfig, SubscriptionPlan, QuestionAttempt


class UserSerializer(serializers.ModelSerializer):
    """User serializer."""
    
    is_premium = serializers.ReadOnlyField()
    active_plans = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'firebase_uid', 'email', 'name', 'exam_type',
            'subscription_tier', 'subscription_expires', 'is_premium', 'active_plans',
            'current_streak', 'max_streak',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans."""
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'key', 'name', 'description', 'price', 'duration_days', 'features', 'is_active']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Subscription serializer."""
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'status', 'started_at',
            'expires_at', 'payment_id', 'amount', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    """Question serializer."""
    
    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'chapter', 'difficulty', 'question_text',
            'options', 'correct_index', 'explanation', 'is_premium',
            'tags', 'image_urls', 'is_pyq', 'year', 'chapter_id', 'subject_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class QuestionListSerializer(serializers.ModelSerializer):
    """Simplified question serializer for list views (without answer)."""
    
    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'chapter', 'difficulty', 'question_text',
            'options', 'correct_index', 'explanation', 'is_premium',
            'tags', 'image_urls', 'is_pyq', 'year', 'chapter_id', 'subject_id'
        ]


class MockTestListSerializer(serializers.ModelSerializer):
    """Mock test serializer for list views."""
    
    question_count = serializers.ReadOnlyField()
    
    class Meta:
        model = MockTest
        fields = [
            'id', 'title', 'description', 'exam_type', 'duration_minutes',
            'total_questions', 'question_count', 'subjects', 'is_featured',
            'is_premium', 'is_previous_year', 'created_at'
        ]


class MockTestDetailSerializer(serializers.ModelSerializer):
    """Mock test serializer with full question details."""
    
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.ReadOnlyField()
    
    class Meta:
        model = MockTest
        fields = [
            'id', 'title', 'description', 'exam_type', 'duration_minutes',
            'total_questions', 'question_count', 'subjects', 'is_featured',
            'is_premium', 'is_previous_year', 'questions', 'created_at', 'updated_at'
        ]



class TestResultSerializer(serializers.ModelSerializer):
    """Test result serializer."""
    
    class Meta:
        model = TestResult
        fields = [
            'id', 'user', 'test_type', 'subject', 'chapter', 'score', 'total_questions',
            'correct_answers', 'time_taken', 'question_reviews', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class QuestionAttemptSerializer(serializers.ModelSerializer):
    """Serializer for question attempts."""
    
    class Meta:
        model = QuestionAttempt
        fields = ['id', 'user', 'question', 'is_correct', 'selected_index', 'attempted_at']
        read_only_fields = ['id', 'user', 'attempted_at']


class UserProgressSerializer(serializers.ModelSerializer):
    """User progress serializer."""
    
    accuracy = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProgress
        fields = [
            'id', 'user', 'subject', 'chapter', 'questions_attempted',
            'correct_answers', 'accuracy', 'last_practiced'
        ]
        read_only_fields = ['id', 'user', 'last_practiced']


class AdConfigSerializer(serializers.ModelSerializer):
    """Ad configuration serializer."""
    
    class Meta:
        model = AdConfig
        fields = ['id', 'ad_unit_id', 'ad_type', 'frequency', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
