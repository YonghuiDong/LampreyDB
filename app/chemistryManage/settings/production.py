# coding: utf-8

from . import *

ENVIRONMENT = 'production'
DEBUG = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'chemical',
        'USER': 'chemical_user',
        'PASSWORD': 'some$-pas8sword',
        'HOST': 'localhost',
        'PORT': '',
    }
}


