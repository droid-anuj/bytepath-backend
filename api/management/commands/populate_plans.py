from django.core.management.base import BaseCommand
from api.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Populates initial subscription plans'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'key': 'CHAPTER_UNLOCK',
                'name': 'Chapter Wise Practice',
                'description': 'Unlock all chapters for practice (Ad-Supported)',
                'price': 179,
                'duration_days': 365,
                'features': ['chapter_unlock']
            },
            {
                'key': 'DAILY_PRACTICE',
                'name': 'Daily Practice',
                'description': 'Daily practice questions (Ad-Free)',
                'price': 249,
                'duration_days': 365,
                'features': ['daily_practice', 'ad_free']
            },
            {
                'key': 'MOCK_TEST_MASTER',
                'name': 'Mock Test Master',
                'description': 'Full length mock tests (Ad-Free)',
                'price': 299,
                'duration_days': 365,
                'features': ['mock_tests', 'ad_free']
            },
            {
                'key': 'CHAPTER_MOCK_COMBO',
                'name': 'Chapter + Mock Combo',
                'description': 'Chapters + Mock Tests (Ad-Free)',
                'price': 449,
                'duration_days': 365,
                'features': ['chapter_unlock', 'mock_tests', 'ad_free']
            },
            {
                'key': 'YEARLY_ELITE',
                'name': 'Yearly Elite',
                'description': 'All features unlocked (Ad-Free)',
                'price': 699,
                'duration_days': 365,
                'features': ['chapter_unlock', 'daily_practice', 'mock_tests', 'ad_free']
            }
        ]

        for plan_data in plans:
            SubscriptionPlan.objects.update_or_create(
                key=plan_data['key'],
                defaults=plan_data
            )
            self.stdout.write(self.style.SUCCESS(f'Updated plan: {plan_data["name"]}'))
