# import os
# from django.conf import settings
#
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# settings.configure(
#     SECRET_KEY='sadfsadfkjl324h5kl23jklj231$@!#$SadfgasdjkfhJKHSJLKADH7234@#',
#     DATABASES={
#         'default': {
#             # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
#             # 'NAME': 'name',
#             # 'USER': 'usr',
#             # 'PASSWORD': 'secret',
#             # 'HOST': '127.0.0.1',
#             # 'PORT': '5432',
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         },
#     },
#     PROXY_CHECKING_PERIOD=1*60,
#     # TIME_ZONE='America/Montreal',
# )

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY='sadfsadfkjl324h5kl23jklj231$@!#$SadfgasdjkfhJKHSJLKADH7234@#',

DATABASES={
    'default': {
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'name',
        # 'USER': 'usr',
        # 'PASSWORD': 'secret',
        # 'HOST': '127.0.0.1',
        # 'PORT': '5432',
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

INSTALLED_APPS=[
    "core",
]

PROXY_CHECKING_PERIOD=10*60

PROXY_PROVIDER_SERVER = {
    'HOST': 'localhost',
    'PORT': 55555,
}