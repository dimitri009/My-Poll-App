
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_DB_IS',
        'USER': 'postgres',
        'PASSWORD': 'Dimitri98!',
        'HOST': 'localhost',
        'PORT': '5432' # (change according to your server settings)
    }
}

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'mbakop4polls@gmail.com'
EMAIL_HOST_PASSWORD = 'kusrcehgqgbakvwg'
EMAIL_PORT = 587 # (change according to your server settings)
EMAIL_USE_TLS = True # (change according to your server settings)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_FROM = 'My Poll App'

BASE_URL = 'http://127.0.0.1:8000/'

SECRET_KEY = 'dimitriromaric16'