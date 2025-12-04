"""
Management command to bulk upload questions from JSON files.
"""

import json
import os
from django.core.management.base import BaseCommand
from api.models import Question


class Command(BaseCommand):
    help = 'Bulk upload questions from JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_files',
            nargs='+',
            type=str,
            help='Paths to JSON files containing questions'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing questions before uploading'
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Question.objects.all().count()
            Question.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing questions'))

        total_created = 0
        total_updated = 0
        total_errors = 0

        for json_file in options['json_files']:
            if not os.path.exists(json_file):
                self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
                continue

            self.stdout.write(f'Processing {json_file}...')

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Handle both single question and array of questions
                questions = data if isinstance(data, list) else [data]

                for q_data in questions:
                    try:
                        # Extract question data
                        question_text = q_data.get('question') or q_data.get('questionText')
                        options_list = q_data.get('options') or q_data.get('choices', [])
                        
                        # Handle different answer formats
                        correct_index = q_data.get('correctIndex')
                        if correct_index is None:
                            correct_answer = q_data.get('correctAnswer') or q_data.get('answer')
                            if isinstance(correct_answer, int):
                                correct_index = correct_answer
                            else:
                                # Find index of correct answer text
                                try:
                                    correct_index = options_list.index(correct_answer)
                                except (ValueError, AttributeError):
                                    correct_index = 0  # Default to first option

                        # Create or update question
                        question, created = Question.objects.update_or_create(
                            question_id=q_data.get('id'),
                            defaults={
                                'question_text': question_text,
                                'subject': q_data.get('subject', 'PHYSICS'),
                                'chapter': q_data.get('chapter', 'Unknown'),
                                'difficulty': q_data.get('difficulty', 'MEDIUM').upper(),
                                'options': options_list,
                                'correct_index': correct_index,
                                'explanation': q_data.get('explanation', ''),
                                'tags': q_data.get('tags', []),
                                'image_urls': q_data.get('imageUrls', []),
                                'is_pyq': q_data.get('isPYQ', False),
                                'year': q_data.get('year'),
                                'chapter_id': q_data.get('chapterId', ''),
                                'subject_id': q_data.get('subjectId', ''),
                                'is_premium': q_data.get('isPremium', False) or q_data.get('is_premium', False),
                            }
                        )

                        if created:
                            total_created += 1
                        else:
                            total_updated += 1

                    except Exception as e:
                        total_errors += 1
                        self.stdout.write(self.style.ERROR(f'Error processing question: {str(e)}'))
                        self.stdout.write(self.style.ERROR(f'Question data: {q_data}'))

            except json.JSONDecodeError as e:
                self.stdout.write(self.style.ERROR(f'Invalid JSON in {json_file}: {str(e)}'))
                total_errors += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {json_file}: {str(e)}'))
                total_errors += 1

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n=== Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Created: {total_created}'))
        self.stdout.write(self.style.SUCCESS(f'Updated: {total_updated}'))
        if total_errors > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {total_errors}'))
        self.stdout.write(self.style.SUCCESS(f'Total processed: {total_created + total_updated}'))
