# FinanceAI Django Project - Complete Setup Guide

## Project Structure

```
financeai/
├── financeai/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── apps.py
│   └── tests.py
├── templates/
│   ├── account/
│   │   ├── login.html
│   │   └── signup.html
│   └── accounts/
│       ├── profile.html
│       └── dashboard.html
├── static/
├── media/
├── .env
├── requirements.txt
├── manage.py
└── README.md
```

## Installation Steps

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Requirements

Create `requirements.txt`:
```
Django>=4.2,<5.0
django-allauth>=0.57.0
python-decouple>=3.8
pillow>=10.0.0
```

Install:
```bash
pip install -r requirements.txt
```

### 3. Create Django Project (if not already created)

```bash
django-admin startproject financeai .
python manage.py startapp accounts
```

### 4. Create .env File

Create `.env` in project root:
```
SECRET_KEY=your-django-secret-key-change-this
DEBUG=True
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

Generate a secret key:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Create Required Directories

```bash
mkdir templates
mkdir templates/account
mkdir templates/accounts
mkdir static
mkdir media
```

### 6. Update Settings

Copy the settings configuration from the first artifact to `financeai/settings.py`

### 7. Update URLs

Copy the URL configuration from the first artifact to `financeai/urls.py`

### 8. Update Models

Copy the models from the first artifact to `accounts/models.py`

### 9. Update Views

Copy the views from the first artifact to `accounts/views.py`

### 10. Update Admin

Copy the admin configuration from the first artifact to `accounts/admin.py`

### 11. Create URLs for Accounts

Copy the URL patterns from the first artifact to `accounts/urls.py`

### 12. Create Templates

Copy the HTML templates to their respective locations:
- `templates/account/login.html`
- `templates/account/signup.html`
- `templates/accounts/profile.html`
- `templates/accounts/dashboard.html`

### 13. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 14. Create Superuser

```bash
python manage.py createsuperuser
```

### 15. Configure Sites Framework

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
site.domain = '127.0.0.1:8000'
site.name = 'FinanceAI'
site.save()
exit()
```

### 16. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Setting Up OAuth (Google & Facebook)

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Configure OAuth consent screen
6. Choose **Web application** as application type
7. Add **Authorized redirect URIs**:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/`
8. Copy **Client ID** and **Client Secret** to `.env` file

### Facebook OAuth Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app (Choose **Consumer** type)
3. Add **Facebook Login** product
4. Go to **Settings** → **Basic**
5. Copy **App ID** and **App Secret** to `.env` file
6. In **Facebook Login** settings, add **Valid OAuth Redirect URIs**:
   - `http://127.0.0.1:8000/accounts/facebook/login/callback/`
   - `http://localhost:8000/accounts/facebook/login/callback/`

### Configure Social Apps in Django Admin

1. Login to admin: http://127.0.0.1:8000/admin/
2. Navigate to **Social applications**
3. Click **Add social application**

**For Google:**
- Provider: Google
- Name: Google OAuth
- Client id: (from Google Console)
- Secret key: (from Google Console)
- Sites: Select your site (127.0.0.1:8000)

**For Facebook:**
- Provider: Facebook
- Name: Facebook Login
- Client id: (Facebook App ID)
- Secret key: (Facebook App Secret)
- Sites: Select your site (127.0.0.1:8000)

## Features

✅ Email/Password Authentication
✅ Google OAuth Login
✅ Facebook OAuth Login
✅ User Registration
✅ Password Reset
✅ User Profile
✅ Dashboard
✅ Social Account Management
✅ Responsive Design
✅ Modern UI/UX

## Available URLs

- `/` - Home (redirects to login)
- `/accounts/login/` - Login page
- `/accounts/signup/` - Signup page
- `/accounts/profile/` - User profile (requires login)
- `/accounts/dashboard/` - Dashboard (requires login)
- `/accounts/logout/` - Logout
- `/accounts/password/reset/` - Password reset
- `/accounts/google/login/` - Google login
- `/accounts/facebook/login/` - Facebook login
- `/admin/` - Admin panel

## Troubleshooting

### Issue: Social login not working

**Solution:** Make sure you've:
1. Added OAuth credentials to `.env`
2. Configured redirect URIs correctly in Google/Facebook
3. Added social applications in Django admin
4. Set correct site domain in Django Sites

### Issue: Templates not found

**Solution:** Check that:
1. `TEMPLATES` `DIRS` includes `BASE_DIR / 'templates'` in settings.py
2. Templates are in correct directories
3. Template names match exactly (case-sensitive)

### Issue: Static files not loading

**Solution:** Run:
```bash
python manage.py collectstatic
```

## Security Considerations for Production

1. Change `DEBUG = False` in production
2. Use a strong, unique `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Use HTTPS for OAuth redirect URIs
5. Set secure cookie settings
6. Use environment variables for sensitive data
7. Enable CSRF protection
8. Use PostgreSQL instead of SQLite

## Next Steps

- Add email verification
- Implement two-factor authentication
- Add more financial features
- Create API endpoints
- Add data visualization
- Implement budgeting features
- Add expense tracking
- Create financial reports

## Support

For issues or questions, please refer to the documentation:
- [Django Documentation](https://docs.djangoproject.com/)
- [Django-allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login Documentation](https://developers.facebook.com/docs/facebook-login/)

---

**Created with ❤️ for FinanceAI**# ai_powered_personal_finance_management
