# PrepShark Backend API

Django REST API backend for PrepShark mobile app with Firebase authentication, premium subscriptions, and payment integration.

## Features

- Firebase Authentication
- REST API for questions, tests, and user management
- Premium subscription system
- Payment integration (Razorpay)
- Ad configuration management
- PostgreSQL database

## Tech Stack

- Django 4.2
- Django REST Framework
- Firebase Admin SDK
- PostgreSQL
- Razorpay

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (create `.env` file):
```
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/prepshark
FIREBASE_CREDENTIALS=path/to/firebase-credentials.json
RAZORPAY_KEY_ID=your-key-id
RAZORPAY_KEY_SECRET=your-key-secret
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run development server:
```bash
python manage.py runserver
```

## API Endpoints

See `/api/docs/` for full API documentation.

## Deployment

Configured for Render.com deployment. See `render.yaml` for configuration.
