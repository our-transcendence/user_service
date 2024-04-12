"""
Django settings for auth project.

Generated by 'django-admin startproject' using Django 4.2.11.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

from login.startup import keygen

from ourJWT import OUR_class, OUR_exception

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bha_z48$lrtojju%5*y5y399k@f%c5!dnu80pbm7u)ccg$l_4y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '82.64.223.220',
    '127.0.0.1'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'auth.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'auth.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "debug": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "mydatabase",
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get("POSTGRES_DB"),
        'HOST': "postgres",
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "PORT": "5432",
    }
}



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PRIVATE_KEY = keygen()

if os.getenv("USER") == "gd-harco":
    print("Using debug local datase")
    DATABASES['default'] = DATABASES["debug"]
else:
    print(f'Using default distant database')

PUBKEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA+UsBSBGi71VYLGUL5nCz
o7NK/VveP2OCqt1SsYrls2OmzyQMs5sjNeVAY3XMf15h5OD5ylCYD8eTILy4PXyD
OShIJyAM6+sfMJh9StKkvkUVRcq+6weg8ueb4obZYddC2YkYAbncjeF2nGQEbG2y
ecZhAXgaPfUZSQqjvCu/haSMo8C5S8+H66jwBV8pv4ewhtdlOV4NM1go7E0BWtgK
6iN8x1PChBsninsfEnyxXME/Ubush7sZ+IKyScXc+87niaR/omlHeL6m/MzsS/qL
tUQzm0UwPhHOBcILO9eGW/DY0W1Hs/8fqSQ5gvcksmS6rShqBb2IxOq2S0eDgCPM
+QIDAQAB
-----END PUBLIC KEY-----"""


encoder: OUR_class.Encoder
decoder: OUR_class.Decoder

try:
    encoder = OUR_class.Encoder(PRIVATE_KEY)
    decoder = OUR_class.Decoder(PUBKEY)
except OUR_exception.NoKey:
    print("NO KEY ERROR")
    exit
