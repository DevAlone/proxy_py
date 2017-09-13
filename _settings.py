import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# change it before deploying
SECRET_KEY = 'sadfsadfkjl324h5kl23jklj231$@!#$SadfgasdjkfhJKHSJLKADH7234@#',

ALLOWED_HOSTS = ['localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'proxy_py',
        'USER': 'proxy_py',
        'PASSWORD': 'proxy_py',
        'HOST': '127.0.0.1',
        'PORT': '5432',
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

INSTALLED_APPS = [
    "core",
]

PROXY_CHECKING_PERIOD = 10*60
BAD_PROXY_CHECKING_PERIOD = 20*60

PROXY_PROVIDER_SERVER = {
    'HOST': 'localhost',
    'PORT': 55555,
}
