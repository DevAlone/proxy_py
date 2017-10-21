import django
from django.conf import settings

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proxy_py.settings")
django.setup()
