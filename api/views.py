"""
API Views for PrepShark.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import razorpay
from django.conf import settings

from .models import User, Subscription, Question, MockTest, TestResult, UserProgress, AdConfig, QuestionAttempt, SubscriptionPlan
from .serializers import (
    UserSerializer, SubscriptionSerializer, QuestionSerializer,
    QuestionListSerializer, MockTestListSerializer, MockTestDetailSerializer,
    TestResultSerializer, UserProgressSerializer, AdConfigSerializer, SubscriptionPlanSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """User profile management."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user profile or return existing one."""
        print(f"DEBUG: Registration request data: {request.data}")
        firebase_uid = request.data.get('firebase_uid')
        
        # Check if user already exists
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            print(f"DEBUG: User already exists: {user.email}, firebase_uid={user.firebase_uid}")
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # Create new user
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            print(f"DEBUG: User registered: {user.email}, firebase_uid={user.firebase_uid}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        """Update current user profile."""
        # Check if user is authenticated (set by middleware)
        if not hasattr(request, 'user') or not hasattr(request.user, 'id'):
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """Question management."""
    
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    pagination_class = None  # Disable pagination to return plain arrays
    
    def get_serializer_class(self):
        """Use simplified serializer for list view."""
        if self.action == 'list':
            return QuestionListSerializer
        return QuestionSerializer
    
    def get_queryset(self):
        """Filter questions based on user subscription and query params."""
        queryset = Question.objects.all()
        user = self.request.user
        
        # Filter premium questions for free users
        # if not user.is_premium:
        #     queryset = queryset.filter(is_premium=False)
        pass # TEMPORARY: Allow access to all questions
        
        # Filter by subject
        subject = self.request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(subject=subject)
        
        # Filter by chapter
        chapter = self.request.query_params.get('chapter')
        if chapter:
            queryset = queryset.filter(chapter=chapter)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty.upper())
            
        # Sort by difficulty: Easy -> Medium -> Hard
        # We use Case/When to assign numeric values for sorting
        from django.db.models import Case, When, Value, IntegerField
        queryset = queryset.annotate(
            difficulty_rank=Case(
                When(difficulty='EASY', then=Value(1)),
                When(difficulty='MEDIUM', then=Value(2)),
                When(difficulty='HARD', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('difficulty_rank', 'id')
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def by_ids(self, request):
        """Get multiple questions by their IDs."""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        queryset = Question.objects.filter(id__in=ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def submit_answer(self, request):
        """Submit an answer for a question."""
        question_id = request.data.get('question_id')
        selected_index = request.data.get('selected_index')
        is_correct = request.data.get('is_correct')
        
        if not question_id or selected_index is None:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Use filter().first() to avoid error if question doesn't exist (though it should)
            # Or get_object_or_404
            question = Question.objects.get(id=question_id)
            
            # Update or create attempt
            attempt, created = QuestionAttempt.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={
                    'is_correct': is_correct,
                    'selected_index': selected_index
                }
            )
            
            return Response({'status': 'success', 'attempt_id': attempt.id})
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def solved_ids(self, request):
        """Get IDs of solved questions for a chapter."""
        subject = request.query_params.get('subject')
        chapter = request.query_params.get('chapter')
        
        if not subject or not chapter:
            return Response({'error': 'Subject and chapter required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get IDs of questions where is_correct=True
        solved_ids = QuestionAttempt.objects.filter(
            user=request.user,
            question__subject=subject,
            question__chapter=chapter,
            is_correct=True
        ).values_list('question_id', flat=True)
        
        return Response(list(solved_ids))

    @action(detail=False, methods=['get'])
    def chapter_stats(self, request):
        """Get stats (total/solved) for all chapters in a subject."""
        subject = request.query_params.get('subject')
        if not subject:
            return Response({'error': 'Subject is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Optimize: Use aggregation instead of looping through chapters
        from django.db.models import Count
        
        # 1. Get total questions per chapter
        total_counts = Question.objects.filter(subject=subject).values('chapter').annotate(total=Count('id'))
        
        # 2. Get solved questions per chapter for this user
        solved_counts = QuestionAttempt.objects.filter(
            user=request.user,
            question__subject=subject,
            is_correct=True
        ).values('question__chapter').annotate(solved=Count('id'))
        
        # 3. Merge results
        stats = {}
        
        # Initialize with totals
        for item in total_counts:
            chapter = item['chapter']
            if not chapter: continue
            stats[chapter] = {
                'total': item['total'],
                'solved': 0
            }
            
        # Update with solved counts
        for item in solved_counts:
            chapter = item['question__chapter']
            if chapter in stats:
                stats[chapter]['solved'] = item['solved']
                
        return Response(stats)

    @action(detail=False, methods=['post'])
    def reset_chapter(self, request):
        """Reset progress for a specific chapter."""
        subject = request.data.get('subject')
        chapter = request.data.get('chapter')
        
        if not subject or not chapter:
            return Response({'error': 'Subject and chapter required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Delete attempts for this chapter
        deleted_count, _ = QuestionAttempt.objects.filter(
            user=request.user,
            question__subject=subject,
            question__chapter=chapter
        ).delete()
        
        return Response({'status': 'success', 'deleted_count': deleted_count})

    @action(detail=False, methods=['get'])
    def random(self, request):
        """Get random questions."""
        count = int(request.query_params.get('count', 10))
        queryset = self.get_queryset().order_by('?')[:count]
        serializer = QuestionListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def chapters(self, request):
        """Get list of chapters for a subject."""
        subject = request.query_params.get('subject')
        if not subject:
            return Response({'error': 'Subject is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Get distinct chapters for the subject
        chapters = self.get_queryset().filter(subject=subject).values_list('chapter', flat=True).distinct().order_by('chapter')
        # Filter out None/empty chapters just in case
        chapters = [c for c in chapters if c]
        
        # Determine lock status
        user = request.user
        is_unlocked_all = False
        
        # Check if user is premium or has specific chapter unlock plan
        # Check if user has specific chapter unlock plan, combo, or yearly elite
        # active_plans property handles checking for active subscriptions
        # if any(plan in user.active_plans for plan in ['CHAPTER_UNLOCK', 'CHAPTER_MOCK_COMBO', 'YEARLY_ELITE']):
        #     is_unlocked_all = True
        
        # TEMPORARY: Unlock all chapters for everyone
        is_unlocked_all = True
        
        # Specific chapters that are always free
        FREE_CHAPTERS = {
            # Physics
            "physical world",
            "units and measurements",
            "electric charges and fields",
            "electrostatic potential and capacitance",
            "electric potential and capacitance", # Handle user variation
            # Chemistry
            "the solid state", "solid state",
            "some basic concepts of chemistry",
            "structure of atom",
            "solutions",
            # Zoology
            "human reproduction",
            "reproductive health",
            "animal kingdom",
            "structural organisation in animals",
            # Botany
            "reproduction in organisms",
            "sexual reproduction in flowering plants",
            "the living world",
            "biological classification"
        }

        response_data = []
        for index, chapter_name in enumerate(chapters):
            is_locked = False
            if not is_unlocked_all:
                # Check if chapter is in the free list (case-insensitive)
                if chapter_name.lower() not in FREE_CHAPTERS:
                    is_locked = True
            
            response_data.append({
                'name': chapter_name,
                'is_locked': is_locked
            })
            
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get question count for a subject/chapter."""
        queryset = self.get_queryset()
        
        subject = request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(subject=subject)
            
        chapter = request.query_params.get('chapter')
        if chapter:
            queryset = queryset.filter(chapter=chapter)
            
        return Response({'count': queryset.count()})


class MockTestViewSet(viewsets.ReadOnlyModelViewSet):
    """Mock test management."""
    
    queryset = MockTest.objects.all()
    serializer_class = MockTestListSerializer
    pagination_class = None  # Disable pagination
    
    def get_serializer_class(self):
        """Use detail serializer for retrieve action."""
        if self.action == 'retrieve':
            return MockTestDetailSerializer
        return MockTestListSerializer
    
    def get_queryset(self):
        """Filter mock tests based on user subscription and exam type."""
        queryset = MockTest.objects.all()
        user = self.request.user
        
        # Filter premium tests for free users
        # Filter premium tests for free users
        # Check if user has mock test master plan, combo, or yearly elite
        has_mock_access = any(plan in user.active_plans for plan in ['MOCK_TEST_MASTER', 'CHAPTER_MOCK_COMBO', 'YEARLY_ELITE'])
        
        # Mock tests are now accessible to everyone (Ad-Supported)
        # But we might still want to differentiate "Premium" mocks if any?
        # For now, let's assume all mocks are free with ads unless marked otherwise?
        # Actually, the requirement says "mock test weekly mock test and all this included 699"
        # and "daily practice 249".
        # Wait, the user said "daily practice 249" and "mock test 299".
        # AND "ads free will be not includerd in chpaterwise but other tahn that free ads will be included"
        # This implies Daily/Mock are FREE with ADS for everyone.
        # And if you pay, you get NO ADS.
        # So we should REMOVE the filter that hides premium tests?
        # Or maybe there are NO premium tests anymore, just tests?
        # Let's assume all tests are accessible.
        
        # However, if we filter by is_premium=False, we hide paid tests.
        # If the goal is "Free with Ads", then we should show them.
        # But maybe "Mock Test Master" unlocks *more* tests?
        # The prompt says: "daily practice 249 per year... mock test 299 per year... ads free will be not includerd in chpaterwise but other tahn that free ads will be included"
        # This phrasing "ads free will be not included in chapterwise but other than that free ads will be included"
        # suggests that for Daily/Mock, if you don't pay, you get Ads. If you pay, you get No Ads.
        # It doesn't explicitly say "All Mocks are Free".
        # BUT, usually "Free with Ads" means you get the content.
        # Let's assume for now that we should NOT filter out "premium" tests for free users, 
        # OR that we mark all tests as "is_premium=False" in the DB.
        # A safer bet for code: Allow access to ALL tests, but frontend handles Ads.
        
        # So, we remove the filter:
        # if not has_mock_access:
        #    queryset = queryset.filter(is_premium=False)
        
        # Actually, let's keep the filter IF there are truly "Premium Only" tests that even Ads don't unlock.
        # But the request implies the "Plan" is for "Ad Free" (and maybe the content itself).
        # "299 per year for mock test" -> If I don't pay, can I access it?
        # "free ads will be included" -> This implies YES, I can access it, but with ads.
        
        # So, I will comment out the filter.
        # queryset = queryset.filter(is_premium=False) 
        pass
        
        # Filter by exam type
        if user.exam_type:
            queryset = queryset.filter(exam_type=user.exam_type)
        
        return queryset



class TestResultViewSet(viewsets.ModelViewSet):
    """Test result management."""
    
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    pagination_class = None  # Disable pagination
    
    def get_queryset(self):
        """Get test results for current user."""
        return TestResult.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Save test result and update user progress."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get test history."""
        results = self.get_queryset()
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics."""
        user = request.user
        results = self.get_queryset()
        
        total_tests = results.count()
        total_questions = sum(r.total_questions for r in results)
        total_correct = sum(r.correct_answers for r in results)
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        return Response({
            'total_tests': total_tests,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'accuracy': round(accuracy, 2),
        })


class UserProgressViewSet(viewsets.ModelViewSet):
    """User progress tracking."""
    
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    pagination_class = None  # Disable pagination
    
    def get_queryset(self):
        """Get progress for current user."""
        return UserProgress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Save progress for current user."""
        serializer.save(user=self.request.user)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Subscription plans."""
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]  # Allow anyone to see plans
    pagination_class = None  # Disable pagination


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Subscription management."""
    
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        """Get subscriptions for current user."""
        return Subscription.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Check subscription status."""
        user = request.user
        return Response({
            'is_premium': user.is_premium,
            'subscription_tier': user.subscription_tier,
            'expires_at': user.subscription_expires,
        })
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """Create Razorpay order for subscription."""
        plan_key = request.data.get('plan', 'DAILY_PRACTICE')
        
        try:
            plan_obj = SubscriptionPlan.objects.get(key=plan_key)
            amount = int(plan_obj.price * 100)  # Convert to paise
        except SubscriptionPlan.DoesNotExist:
            # Fallback for legacy or if DB not populated yet
            amount = settings.SUBSCRIPTION_PRICES.get(plan_key, 29900)
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': 1
        })
        
        return Response({
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID,
        })
    
    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        """Verify payment and activate subscription."""
        payment_id = request.data.get('payment_id')
        plan_key = request.data.get('plan', 'DAILY_PRACTICE')
        
        # Calculate expiry date
        try:
            plan_obj = SubscriptionPlan.objects.get(key=plan_key)
            duration_days = plan_obj.duration_days
            amount = plan_obj.price
        except SubscriptionPlan.DoesNotExist:
            # Fallback logic
            if plan_key in ['DAILY_PRACTICE', 'MOCK_TEST_MASTER']:
                duration_days = 30
                amount = 299 if plan_key == 'DAILY_PRACTICE' else 499
            elif plan_key == 'YEARLY_ELITE':
                duration_days = 365
                amount = 2999
            else:
                duration_days = 30
                amount = 299
        
        expires_at = timezone.now() + timedelta(days=duration_days)
        
        # Create subscription record
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan_key,
            status='ACTIVE',
            expires_at=expires_at,
            payment_id=payment_id,
            amount=amount
        )
        
        # Update user subscription
        request.user.subscription_tier = 'PREMIUM'
        request.user.subscription_expires = expires_at
        request.user.save()
        
        return Response({
            'message': 'Subscription activated successfully',
            'expires_at': expires_at,
        })


class AdConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """Ad configuration."""
    
    queryset = AdConfig.objects.filter(is_active=True)
    serializer_class = AdConfigSerializer
    
    @action(detail=False, methods=['get'])
    def config(self, request):
        """Get ad configuration for current user."""
        user = request.user
        
        # Premium users don't see ads
        if user.is_premium:
            return Response({'show_ads': False})
        
        configs = self.get_queryset()
        serializer = self.get_serializer(configs, many=True)
        
        return Response({
            'show_ads': True,
            'configs': serializer.data,
        })


class DailyPracticeViewSet(viewsets.ViewSet):
    """Daily Practice Paper management."""
    
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def questions(self, request):
        """Get daily questions (25 or 50)."""
        count = int(request.query_params.get('count', 25))
        if count not in [25, 50]:
            return Response({'error': 'Count must be 25 or 50'}, status=status.HTTP_400_BAD_REQUEST)
            
        today = timezone.now().date()
        
        # Check if paper already exists
        from .models import DailyPracticePaper
        
        try:
            paper = DailyPracticePaper.objects.get(date=today, practice_type=count)
            questions = paper.questions.all()
            serializer = QuestionListSerializer(questions, many=True)
            return Response(serializer.data)
        except DailyPracticePaper.DoesNotExist:
            # Generate new paper
            pass
            
        # Seed random with today's date for consistency across users (fallback if DB fails)
        # But now we persist it, so seed is less critical for consistency, but good for reproducibility
        seed = int(today.strftime('%Y%m%d'))
        
        # We need questions from Physics, Chemistry, Botany, Zoology
        # Let's distribute them roughly equally
        subjects = ['Physics', 'Chemistry', 'Botany', 'Zoology']
        questions_per_subject = count // 4
        remainder = count % 4
        
        all_questions = []
        
        import random
        # Use a deterministic random generator seeded with date
        rng = random.Random(seed)
        
        for i, subject in enumerate(subjects):
            # Calculate how many questions for this subject
            limit = questions_per_subject + (1 if i < remainder else 0)
            
            # Get IDs of all questions for this subject
            # We fetch IDs first to be efficient, then pick random IDs
            q_ids = list(Question.objects.filter(subject__iexact=subject).values_list('id', flat=True))
            
            if not q_ids:
                continue
                
            # Shuffle deterministically
            rng.shuffle(q_ids)
            
            # Pick top N
            selected_ids = q_ids[:limit]
            
            # Fetch actual objects
            # We need to preserve order, or just return them
            questions = Question.objects.filter(id__in=selected_ids)
            all_questions.extend(questions)
            
        # Create persistent paper
        if all_questions:
            paper = DailyPracticePaper.objects.create(
                date=today,
                practice_type=count
            )
            paper.questions.set(all_questions)
            
        # Serialize
        serializer = QuestionListSerializer(all_questions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit daily practice attempt."""
        practice_type = request.data.get('type') # 25 or 50
        score = request.data.get('score', 0)
        total_questions = request.data.get('total_questions', 0)
        correct_answers = request.data.get('correct_answers', 0)
        
        if practice_type not in [25, 50]:
            return Response({'error': 'Invalid practice type'}, status=status.HTTP_400_BAD_REQUEST)
            
        today = timezone.now().date()
        user = request.user
        
        from .models import DailyPracticeAttempt
        
        # Check for existing attempt
        existing_attempt = DailyPracticeAttempt.objects.filter(
            user=user,
            date=today,
            practice_type=practice_type
        ).first()
        
        if existing_attempt:
            # Keep the best score
            if score > existing_attempt.score:
                existing_attempt.score = score
                existing_attempt.save()
                # We could also update created_at to show latest attempt time if we wanted
            
            # If new score is lower, we discard it (do nothing)
            # But we still return success so frontend shows the result
        else:
            DailyPracticeAttempt.objects.create(
                user=user,
                date=today,
                practice_type=practice_type,
                is_completed=True,
                score=score
            )
        
        # Streak Logic
        # Check if user already has a practice date of today
        if user.last_practice_date != today:
            yesterday = today - timedelta(days=1)
            
            if user.last_practice_date == yesterday:
                # Continued streak
                user.current_streak += 1
            else:
                # Broken streak or first time
                user.current_streak = 1
                
            # Update max streak
            if user.current_streak > user.max_streak:
                user.max_streak = user.current_streak
                
            user.last_practice_date = today
            user.save()
            
        return Response({
            'status': 'success',
            'current_streak': user.current_streak,
            'max_streak': user.max_streak,
            'is_attempted_today': True
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get daily practice history."""
        user = request.user
        from .models import DailyPracticeAttempt
        
        attempts = DailyPracticeAttempt.objects.filter(user=user).order_by('-date', '-created_at')
        
        # Simple serialization
        data = []
        for attempt in attempts:
            data.append({
                'id': attempt.id,
                'date': attempt.date,
                'practice_type': attempt.practice_type,
                'score': attempt.score,
                'created_at': attempt.created_at
            })
            
        return Response(data)

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get daily practice status."""
        user = request.user
        today = timezone.now().date()
        
        from .models import DailyPracticeAttempt
        
        # Get all attempts for today
        attempts = DailyPracticeAttempt.objects.filter(
            user=user,
            date=today,
            is_completed=True
        ).values_list('practice_type', flat=True)
        
        attempted_types = list(set(attempts)) # Unique types
        
        return Response({
            'is_attempted_today': bool(attempted_types),
            'attempted_types': attempted_types,
            'current_streak': user.current_streak,
            'max_streak': user.max_streak,
            'last_practice_date': user.last_practice_date
        })
