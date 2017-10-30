import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# change it before deploying
SECRET_KEY = 'sadfsadfkjl324h5kl23jklj231$@!#$SadfgasdjkfhJKHSJLKADH7234@#',

ALLOWED_HOSTS = []  # ['localhost']
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

INSTALLED_APPS = [
    "core.apps.CoreConfig",
]

# ROOT_URLCONF = "proxy_py.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


# WSGI_APPLICATION = 'proxy_py.wsgi.application'
# STATIC_URL = '/static/'

# fetcher settings

PROXY_CHECKING_PERIOD = 10 * 60
BAD_PROXY_CHECKING_PERIOD = 60 * 60

PROXY_PROVIDER_SERVER_ADDRESS = {
    'HOST': 'localhost',
    'PORT': 55555,
}

PROXY_PROVIDER_SERVER_API_CONFIG = {
    'proxy': {
        'modelClass': ('core.models', 'Proxy'),
        'methods': {
            'get': {
                'fields': ['address', 'protocol', 'auth_data', 'domain', 'port', 'white_ip_v4', 'white_ip_v6',
                           'last_check_time', 'number_of_bad_checks', 'bad_proxy', 'uptime'],
                'filterFields': ['white_ip_v4', 'white_ip_v6', 'last_check_time', 'protocol', 'number_of_bad_checks',
                                 'bad_proxy', 'uptime'],
                'orderFields': ['last_check_time', 'number_of_bad_checks', 'uptime'],
            }
        }
    }
}
