# Production Settings for Render Deployment

## Environment Variables to Set in Render Dashboard

Copy these and set them in your Render web service:

### Required Variables

```bash
# Django Secret Key (generate a new one!)
DJANGO_SECRET_KEY=your-super-secret-key-change-this-to-random-string

# Debug Mode (MUST be False in production)
DEBUG=False

# Allowed Hosts
ALLOWED_HOSTS=.onrender.com,prepshark-api.onrender.com

# Database URL (automatically provided by Render PostgreSQL)
DATABASE_URL=<will-be-auto-filled-by-render>

# Firebase Credentials Path
FIREBASE_CREDENTIALS=/etc/secrets/serviceAccountKey.json

# Razorpay Credentials
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# CORS Origins (update with your actual domain/app)
CORS_ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com
```

### Optional Variables

```bash
# Python Version
PYTHON_VERSION=3.11.0
```

---

## Secret Files to Upload

Upload these files in Render Dashboard → Environment → Secret Files:

### 1. Firebase Service Account Key

**Filename**: `/etc/secrets/serviceAccountKey.json`

**Content**: Copy the entire content of your `serviceAccountKey.json` file

---

## Build & Start Commands

### Build Command
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start Command
```bash
gunicorn config.wsgi:application
```

---

## Database Configuration

### PostgreSQL Database Settings

- **Name**: `prepshark-db`
- **Database**: `prepshark`
- **User**: `prepshark`
- **Region**: Singapore (or closest to your users)
- **Plan**: Free

The `DATABASE_URL` will be automatically set by Render.

---

## Post-Deployment Steps

### 1. Import Data

After successful deployment, you need to import your SQLite data:

**Option A: Using Render Shell**
1. Go to Render Dashboard → Your Service → Shell
2. Upload `data_backup.json` (you can use the file upload feature)
3. Run:
   ```bash
   python manage.py loaddata data_backup.json
   ```

**Option B: Using Render CLI** (if installed)
```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Upload and import
render shell prepshark-api
# Then run: python manage.py loaddata data_backup.json
```

### 2. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 3. Verify Deployment

Test these endpoints:
- `https://your-app.onrender.com/api/` - Should return API info
- `https://your-app.onrender.com/admin/` - Admin panel
- `https://your-app.onrender.com/api/questions/` - Questions endpoint

---

## Important Notes

⚠️ **Free Tier Limitations**:
- Database: Free for 90 days, then $7/month
- Web Service: Spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds

💡 **Tips**:
- Keep `data_backup.json` safe - it's your complete database backup
- Don't commit `serviceAccountKey.json` to Git
- Generate a strong `DJANGO_SECRET_KEY` for production
- Update `CORS_ALLOWED_ORIGINS` with your actual Flutter app domain

---

## Troubleshooting

### Build Fails
- Check requirements.txt is up to date
- Verify Python version compatibility
- Check build logs for specific errors

### Database Connection Fails
- Ensure PostgreSQL database is created
- Verify DATABASE_URL is set correctly
- Check database and web service are in same region

### Static Files Not Loading
- Verify `collectstatic` ran in build command
- Check `whitenoise` is in MIDDLEWARE
- Ensure STATIC_ROOT is set correctly

### Firebase Authentication Fails
- Verify serviceAccountKey.json is uploaded correctly
- Check file path matches FIREBASE_CREDENTIALS variable
- Ensure file content is valid JSON

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `DJANGO_SECRET_KEY` generated
- [ ] `serviceAccountKey.json` not in Git
- [ ] `.env` file not in Git
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS properly configured
- [ ] Database credentials secure

---

## Next Steps After Deployment

1. Update Flutter app API URL to your Render URL
2. Test all endpoints from Flutter app
3. Monitor logs for errors
4. Set up regular database backups
5. Consider upgrading to paid plan for production use
