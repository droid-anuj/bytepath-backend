# PrepShark Django Backend - Setup Guide

## 🚀 Quick Start

### 1. Create Virtual Environment
```bash
cd prepshark-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual values
```

### 4. Get Firebase Credentials
1. Go to Firebase Console
2. Project Settings → Service Accounts
3. Generate new private key
4. Save as `firebase-credentials.json` in project root
5. Update `.env` with the path

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin/

## 📡 API Endpoints

### Authentication
- POST `/api/users/register/` - Register user
- GET `/api/users/profile/` - Get profile
- PATCH `/api/users/update_profile/` - Update profile

### Questions
- GET `/api/questions/` - List questions
- GET `/api/questions/{id}/` - Get question
- GET `/api/questions/random/?count=10` - Random questions

### Tests
- POST `/api/tests/` - Submit test result
- GET `/api/tests/history/` - Test history
- GET `/api/tests/stats/` - User statistics

### Subscriptions
- GET `/api/subscriptions/status/` - Check status
- POST `/api/subscriptions/create_order/` - Create payment
- POST `/api/subscriptions/verify_payment/` - Verify payment

### Ads
- GET `/api/ads/config/` - Get ad configuration

## 🚢 Deployment to Render.com

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. Create Render Account
- Go to https://render.com
- Sign up with GitHub

### 3. Create PostgreSQL Database
- New → PostgreSQL
- Name: prepshark-db
- Free tier
- Copy connection string

### 4. Create Web Service
- New → Web Service
- Connect repository
- Name: prepshark-api
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start Command: `gunicorn config.wsgi:application`

### 5. Add Environment Variables
```
DJANGO_SECRET_KEY=<generate-random-key>
DEBUG=False
DATABASE_URL=<from-step-3>
FIREBASE_CREDENTIALS=<paste-json-content>
RAZORPAY_KEY_ID=<your-key>
RAZORPAY_KEY_SECRET=<your-secret>
```

### 6. Deploy!
- Click "Create Web Service"
- Wait for deployment
- Your API will be live at: `https://prepshark-api.onrender.com`

## 🧪 Testing

### Test API with curl
```bash
# Get questions
curl -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  https://prepshark-api.onrender.com/api/questions/

# Submit test
curl -X POST \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test_type":"CHAPTER","score":80,"total_questions":10}' \
  https://prepshark-api.onrender.com/api/tests/
```

## 📝 Next Steps

1. Add sample questions via Django admin
2. Test all endpoints
3. Update Flutter app to use new API
4. Set up Razorpay account
5. Configure AdMob

## 🆘 Troubleshooting

### Database connection error
- Check DATABASE_URL in .env
- Ensure PostgreSQL is running

### Firebase auth error
- Verify firebase-credentials.json path
- Check Firebase project settings

### Import errors
- Activate virtual environment
- Run `pip install -r requirements.txt`

## 📚 Resources

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Render Docs: https://render.com/docs
- Razorpay Docs: https://razorpay.com/docs/
