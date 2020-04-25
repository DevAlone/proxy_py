from broker import settings as broker
from proxies_handler import settings as proxies_handler
from tasks_handler import settings as tasks_handler
from results_handler import settings as results_handler

try:
    from user_settings import *
except ModuleNotFoundError:
    from default_settings import *
