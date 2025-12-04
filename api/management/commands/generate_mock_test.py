import os
import json
import random
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Question, MockTest

class Command(BaseCommand):
    help = 'Generates a full syllabus mock test from JSON question files'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1, help='Number of mock tests to generate')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        self.stdout.write(f'Starting generation of {count} mock tests...')

        # Configuration
        questions_dir = os.path.join(settings.BASE_DIR, 'questions')
        target_subjects = ['Physics', 'Chemistry', 'Botany', 'Zoology']
        questions_per_subject = 45
        
        # Storage for questions
        subject_questions = {subject: [] for subject in target_subjects}
        
        # 1. Load all questions from JSON files
        if not os.path.exists(questions_dir):
            self.stdout.write(self.style.ERROR(f'Questions directory not found: {questions_dir}'))
            return

        json_files = [f for f in os.listdir(questions_dir) if f.endswith('.json')]
        self.stdout.write(f'Found {len(json_files)} JSON files.')

        for filename in json_files:
            file_path = os.path.join(questions_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Handle both list of questions and object with 'questions' key
                    questions_list = []
                    if isinstance(data, list):
                        questions_list = data
                    elif isinstance(data, dict) and 'questions' in data:
                        questions_list = data['questions']
                    
                    for q_data in questions_list:
                        # Normalize subject
                        subject = q_data.get('subject', '')
                        # Map sub-subjects if necessary (e.g., Organic Chemistry -> Chemistry)
                        if 'Physics' in subject: subject = 'Physics'
                        elif 'Chemistry' in subject: subject = 'Chemistry'
                        elif 'Botany' in subject: subject = 'Botany'
                        elif 'Zoology' in subject: subject = 'Zoology'
                        elif 'Biology' in subject:
                            pass
                        
                        if subject in target_subjects:
                            subject_questions[subject].append(q_data)
                            
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error reading {filename}: {e}'))

        # Loop for number of tests
        for i in range(count):
            self.stdout.write(f'Generating test {i+1}/{count}...')
            
            # 2. Select random questions and save to DB
            selected_questions = []
            
            for subject in target_subjects:
                available = subject_questions[subject]
                available_count = len(available)
                
                if available_count < questions_per_subject:
                    self.stdout.write(self.style.WARNING(f'Not enough questions for {subject}. Taking all {available_count}.'))
                    selected = available
                else:
                    selected = random.sample(available, questions_per_subject)
                
                # Save/Get questions in DB
                for q_data in selected:
                    question_obj = self._get_or_create_question(q_data)
                    selected_questions.append(question_obj)

            # 3. Create Mock Test
            if not selected_questions:
                self.stdout.write(self.style.ERROR('No questions selected. Skipping.'))
                continue

            mock_test = MockTest.objects.create(
                title=f'Full Syllabus Mock Test {random.randint(1000, 9999)}',
                description='Automatically generated full syllabus mock test covering Physics, Chemistry, Botany, and Zoology.',
                exam_type='NEET', # Defaulting to NEET based on subjects
                duration_minutes=180, # 3 hours
                total_questions=len(selected_questions),
                is_featured=False, # Only feature the first one or none
                is_premium=False,
                subjects=target_subjects
            )
            
            mock_test.questions.set(selected_questions)
            mock_test.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully created Mock Test: "{mock_test.title}" (ID: {mock_test.id}) with {mock_test.questions.count()} questions.'))

    def _get_or_create_question(self, data):
        """Helper to create question object from JSON data."""
        # Map JSON keys to Model fields
        # JSON: id, question, options, correctIndex, difficulty, explanation, subject, chapter, tags...
        # Model: question_id, question_text, options, correct_index, difficulty, explanation, subject, chapter...
        
        question_id = data.get('id')
        
        # Try to find existing question
        if question_id:
            existing = Question.objects.filter(question_id=question_id).first()
            if existing:
                return existing

        # Create new
        return Question.objects.create(
            question_id=question_id,
            question_text=data.get('question', ''),
            options=data.get('options', []),
            correct_index=data.get('correctIndex', 0),
            difficulty=data.get('difficulty', 'MEDIUM').upper(),
            explanation=data.get('explanation', ''),
            subject=data.get('subject', 'Unknown'),
            chapter=data.get('chapter', 'Unknown'),
            tags=data.get('tags', []),
            image_urls=data.get('imageUrls', []),
            is_pyq=data.get('isPYQ', False),
            year=data.get('year'),
            chapter_id=data.get('chapterId', ''),
            subject_id=data.get('subjectId', '')
        )
