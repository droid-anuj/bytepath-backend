import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import User, Subscription

def verify_active_plans():
    # Create a test user
    email = "test_plans@example.com"
    user, created = User.objects.get_or_create(email=email, defaults={'name': 'Test User', 'firebase_uid': 'test_uid_plans'})
    
    # Clear existing subscriptions
    Subscription.objects.filter(user=user).delete()
    
    print(f"User: {user.email}")
    print(f"Initial Active Plans: {user.active_plans}")
    assert user.active_plans == []
    
    # Add Chapter Unlock Plan
    Subscription.objects.create(
        user=user,
        plan='CHAPTER_UNLOCK',
        status='ACTIVE',
        expires_at=timezone.now() + timedelta(days=30),
        payment_id='test_pay_1',
        amount=199
    )
    
    # Refresh user
    user.refresh_from_db()
    print(f"After Chapter Unlock: {user.active_plans}")
    assert 'CHAPTER_UNLOCK' in user.active_plans
    
    # Add Mock Test Plan
    Subscription.objects.create(
        user=user,
        plan='MOCK_TEST_MASTER',
        status='ACTIVE',
        expires_at=timezone.now() + timedelta(days=30),
        payment_id='test_pay_2',
        amount=299
    )
    
    user.refresh_from_db()
    print(f"After Mock Test: {user.active_plans}")
    assert 'CHAPTER_UNLOCK' in user.active_plans
    assert 'MOCK_TEST_MASTER' in user.active_plans
    
    # Add Yearly Elite (Premium)
    Subscription.objects.create(
        user=user,
        plan='YEARLY_ELITE',
        status='ACTIVE',
        expires_at=timezone.now() + timedelta(days=365),
        payment_id='test_pay_3',
        amount=999
    )
    
    user.refresh_from_db()
    print(f"After Yearly Elite: {user.active_plans}")
    assert 'YEARLY_ELITE' in user.active_plans
    print(f"Is Premium (Legacy Check): {user.is_premium}")
    assert user.is_premium == True
    
    print("\n✅ Verification Successful!")

if __name__ == '__main__':
    verify_active_plans()
