# Deployment Checklist

## Pre-Deployment

- [ ] Export SQLite data: `./export_data.sh`
- [ ] Convert Firebase credentials: `./convert_firebase_creds.sh`
- [ ] Update `.gitignore` (exclude `.env`, `db.sqlite3`, `serviceAccountKey.json`)
- [ ] Test locally with PostgreSQL (optional but recommended)
- [ ] Commit all changes to Git
- [ ] Push to GitHub

## Render Deployment

### Database Setup
- [ ] Create PostgreSQL database on Render
- [ ] Note down database connection string
- [ ] Verify database is in same region as web service

### Web Service Setup
- [ ] Connect GitHub repository
- [ ] Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- [ ] Set start command: `gunicorn config.wsgi:application`
- [ ] Select Python 3.11 environment

### Environment Variables
- [ ] `DJANGO_SECRET_KEY` (generate new one)
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS=.onrender.com`
- [ ] `DATABASE_URL` (from PostgreSQL database)
- [ ] `FIREBASE_CREDENTIALS=/etc/secrets/serviceAccountKey.json`
- [ ] `RAZORPAY_KEY_ID`
- [ ] `RAZORPAY_KEY_SECRET`
- [ ] `CORS_ALLOWED_ORIGINS` (your Flutter app URL)

### Secret Files
- [ ] Upload `serviceAccountKey.json` to `/etc/secrets/serviceAccountKey.json`

### Deploy
- [ ] Click "Manual Deploy"
- [ ] Wait for build to complete
- [ ] Check logs for errors

## Railway Deployment

### Database Setup
- [ ] Add PostgreSQL database
- [ ] Note `DATABASE_URL` is auto-created

### Service Setup
- [ ] Connect GitHub repository
- [ ] Railway auto-detects Django
- [ ] Verify build/start commands

### Environment Variables
- [ ] `DJANGO_SECRET_KEY`
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS=.railway.app`
- [ ] `FIREBASE_CREDENTIALS_BASE64` (from convert_firebase_creds.sh)
- [ ] `RAZORPAY_KEY_ID`
- [ ] `RAZORPAY_KEY_SECRET`
- [ ] `CORS_ALLOWED_ORIGINS`

### Deploy
- [ ] Railway auto-deploys on push
- [ ] Monitor deployment logs

## Post-Deployment

### Data Migration
- [ ] Access production shell/CLI
- [ ] Run: `python manage.py migrate`
- [ ] Upload `data_backup.json`
- [ ] Run: `python manage.py loaddata data_backup.json`
- [ ] Verify data loaded correctly

### Testing
- [ ] Test API endpoint: `curl https://your-app.onrender.com/api/`
- [ ] Access admin panel: `https://your-app.onrender.com/admin/`
- [ ] Test authentication with Firebase
- [ ] Test question retrieval
- [ ] Test mock tests
- [ ] Test user registration/login
- [ ] Verify Razorpay integration

### Flutter App Update
- [ ] Update API base URL in `lib/services/api_service.dart`
- [ ] Test from Flutter app
- [ ] Verify all features work

## Monitoring

- [ ] Set up error monitoring (Sentry recommended)
- [ ] Monitor database usage
- [ ] Check response times
- [ ] Review logs regularly

## Backup Strategy

- [ ] Set up automated database backups
- [ ] Export data weekly: `python manage.py dumpdata > backup_$(date +%Y%m%d).json`
- [ ] Store backups securely (Google Drive, S3, etc.)

## Security

- [ ] Ensure `DEBUG=False` in production
- [ ] Verify HTTPS is enabled
- [ ] Check CORS settings
- [ ] Review allowed hosts
- [ ] Rotate secret keys regularly
- [ ] Keep dependencies updated

## Performance

- [ ] Enable database connection pooling
- [ ] Set up CDN for static files (optional)
- [ ] Monitor database query performance
- [ ] Consider caching (Redis) if needed

## Notes

- Render free tier: Database sleeps after 90 days of inactivity
- Railway free tier: $5 credit per month
- Both platforms support custom domains
- SSL/HTTPS is automatic

## Troubleshooting

If deployment fails:
1. Check build logs
2. Verify all environment variables are set
3. Ensure requirements.txt is up to date
4. Check database connection string
5. Verify Firebase credentials are uploaded correctly

## Support

- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
