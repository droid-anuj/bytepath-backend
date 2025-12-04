# PrepShark Backend - Quick Reference

## 🚀 Local Development

### Start Server
```bash
cd prepshark-backend
source venv/bin/activate
python manage.py runserver
```

### Access Points
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Root**: http://127.0.0.1:8000/api/
- **Login**: username: `admin`, password: `admin123`

## 📝 Common Commands

### Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Shell
```bash
python manage.py shell
```

## 📡 API Endpoints

### Questions
- `GET /api/questions/` - List all questions
- `GET /api/questions/?subject=Physics` - Filter by subject
- `GET /api/questions/random/?count=10` - Random questions

### Tests
- `POST /api/tests/` - Submit test result
- `GET /api/tests/stats/` - User statistics

### Subscriptions
- `GET /api/subscriptions/status/` - Check subscription
- `POST /api/subscriptions/create_order/` - Create payment

## 🔐 Authentication

API endpoints require Firebase token:
```
Authorization: Bearer <firebase-token>
```

Admin panel uses Django authentication (no token needed).

## 🚢 Deployment

See `SETUP.md` for full deployment guide to Render.com.

## 📚 Documentation

- `README.md` - Project overview
- `SETUP.md` - Setup guide
- `render.yaml` - Deployment config
