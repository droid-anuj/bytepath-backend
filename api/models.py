"""
Database models for PrepShark API.
"""

from django.db import models
from django.utils import timezone


class User(models.Model):
    """User profile model."""
    
    EXAM_CHOICES = [
        ('JEE', 'JEE'),
        ('NEET', 'NEET'),
    ]
    
    SUBSCRIPTION_CHOICES = [
        ('FREE', 'Free'),
        ('PREMIUM', 'Premium'),
    ]
    
    firebase_uid = models.CharField(max_length=128, unique=True, db_index=True)
    email = models.EmailField()
    name = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=10, choices=EXAM_CHOICES)
    subscription_tier = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='FREE')
    subscription_expires = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Streak Tracking
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    last_practice_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def is_authenticated(self):
        """Always return True for this user model as it represents a logged-in user."""
        return True

    @property
    def is_anonymous(self):
        """Always return False for this user model."""
        return False
    
    @property
    def is_premium(self):
        """Check if user has active premium subscription (Yearly Elite)."""
        # Kept for backward compatibility, now checks for YEARLY_ELITE
        return 'YEARLY_ELITE' in self.active_plans

    @property
    def active_plans(self):
        """Get list of active subscription plan keys."""
        # Get all active, non-expired subscriptions
        active_subs = self.subscriptions.filter(
            status='ACTIVE',
            expires_at__gt=timezone.now()
        ).values_list('plan', flat=True)
        
        plans = set(active_subs)
        
        # If user has YEARLY_ELITE, they effectively have all plans
        # But we'll just return what they have. The checks should handle the hierarchy.
        # Or we can explicitly add others if YEARLY_ELITE is present?
        # Better to keep it simple: return what is active. The consumer checks for specific OR elite.
        
        return list(plans)



class DailyPracticeAttempt(models.Model):
    """Track daily practice attempts."""
    
    TYPE_CHOICES = [
        (25, 'Daily 25'),
        (50, 'Daily 50'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_attempts')
    date = models.DateField(default=timezone.now)
    practice_type = models.IntegerField(choices=TYPE_CHOICES)
    is_completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_practice_attempts'
        ordering = ['-date', '-created_at']
        unique_together = ['user', 'date', 'practice_type'] # One attempt per type per day? Or just one per day?
        # User requirement: "streak will on the bassis of this either daily 25 question attempte or 50 dialy question attempted"
        # So completing either counts. 
        # But can they do both? Probably yes.
    
    def __str__(self):
        return f"{self.user.name} - {self.date} ({self.practice_type})"


class SubscriptionPlan(models.Model):
    """Subscription plan configuration."""
    
    key = models.CharField(max_length=50, unique=True, help_text="Unique key e.g. DAILY_PRACTICE")
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in INR")
    duration_days = models.IntegerField(help_text="Duration in days")
    features = models.JSONField(default=list, blank=True, help_text="List of features")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} (₹{self.price})"


class Subscription(models.Model):
    """Subscription payment records."""
    
    PLAN_CHOICES = [
        ('DAILY_PRACTICE', 'Daily Practice'),
        ('MOCK_TEST_MASTER', 'Mock Test Master'),
        ('YEARLY_ELITE', 'Yearly Elite'),
        ('CHAPTER_UNLOCK', 'Chapter Wise Practice'),
        ('CHAPTER_MOCK_COMBO', 'Chapter + Mock Combo'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    payment_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.plan} ({self.status})"


class Question(models.Model):
    """Question model for practice and tests."""
    
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]
    
    subject = models.CharField(max_length=100)
    chapter = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    
    question_text = models.TextField()
    options = models.JSONField()  # List of options
    correct_index = models.IntegerField()  # Index of correct answer
    explanation = models.TextField(blank=True)
    
    # Additional metadata
    question_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Original ID from JSON
    tags = models.JSONField(default=list, blank=True)  # List of tags
    image_urls = models.JSONField(default=list, blank=True)  # List of image URLs
    is_pyq = models.BooleanField(default=False)  # Previous Year Question
    year = models.IntegerField(null=True, blank=True)  # Year of question
    chapter_id = models.CharField(max_length=255, blank=True)
    subject_id = models.CharField(max_length=255, blank=True)
    
    is_premium = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'chapter']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.chapter} ({self.difficulty})"


class MockTest(models.Model):
    """Mock test model for full-length practice tests."""
    
    EXAM_TYPE_CHOICES = [
        ('JEE', 'JEE Main'),
        ('NEET', 'NEET'),
        ('BOARD', 'Board Exam'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    
    duration_minutes = models.IntegerField(help_text="Test duration in minutes")
    total_questions = models.IntegerField()
    questions = models.ManyToManyField(Question, related_name='mock_tests')
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    is_previous_year = models.BooleanField(default=False)
    
    subjects = models.JSONField(default=list, help_text="List of subjects covered")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['exam_type', 'is_featured']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.exam_type})"
    
    @property
    def question_count(self):
        """Get actual number of questions."""
        return self.questions.count()


class DailyPracticePaper(models.Model):
    """Daily Practice Paper containing questions for a specific date."""
    date = models.DateField()
    practice_type = models.IntegerField(choices=[(25, 'Daily 25'), (50, 'Daily 50')])
    questions = models.ManyToManyField(Question, related_name='daily_papers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['date', 'practice_type']
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - Daily {self.practice_type}"




class TestResult(models.Model):
    """Test result records."""
    
    TEST_TYPE_CHOICES = [
        ('CHAPTER', 'Chapter Practice'),
        ('MOCK', 'Mock Test'),
        ('CUSTOM', 'Custom Test'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    test_type = models.CharField(max_length=10, choices=TEST_TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True)  # Added for history display
    chapter = models.CharField(max_length=255, blank=True)  # Added for history display
    score = models.IntegerField()
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    time_taken = models.IntegerField()  # in seconds
    question_reviews = models.JSONField()  # Array of question review data
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'test_results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.name} - {self.test_type} ({self.score}/{self.total_questions})"


class UserProgress(models.Model):
    """Track user progress per chapter."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    subject = models.CharField(max_length=50)
    chapter = models.CharField(max_length=100)
    questions_attempted = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    last_practiced = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_progress'
        unique_together = ['user', 'subject', 'chapter']
        ordering = ['-last_practiced']
    
    def __str__(self):
        return f"{self.user.name} - {self.subject}/{self.chapter}"
    
    @property
    def accuracy(self):
        """Calculate accuracy percentage."""
        if self.questions_attempted == 0:
            return 0
        return (self.correct_answers / self.questions_attempted) * 100


class QuestionAttempt(models.Model):
    """Track individual question attempts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_attempts')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempts')
    is_correct = models.BooleanField()
    selected_index = models.IntegerField()
    attempted_at = models.DateTimeField(auto_now=True)  # Updates on every attempt

    class Meta:
        db_table = 'question_attempts'
        unique_together = ['user', 'question']  # One record per question per user
        ordering = ['-attempted_at']

    def __str__(self):
        status = "Correct" if self.is_correct else "Incorrect"
        return f"{self.user.name} - {self.question.id} ({status})"


class AdConfig(models.Model):
    """Ad configuration model."""
    
    AD_TYPE_CHOICES = [
        ('BANNER', 'Banner'),
        ('INTERSTITIAL', 'Interstitial'),
        ('REWARDED', 'Rewarded'),
    ]
    
    ad_unit_id = models.CharField(max_length=255)
    ad_type = models.CharField(max_length=15, choices=AD_TYPE_CHOICES)
    frequency = models.IntegerField(default=5)  # Show after N questions
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ad_configs'
    
    def __str__(self):
        return f"{self.ad_type} - {self.ad_unit_id}"
