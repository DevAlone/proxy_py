import os

DATABASE_CONNECTION_ARGS = (
    'sqlite:///db.sqlite3',
)

DATABASE_CONNECTION_KWARGS = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# fetcher settings

CONCURRENT_TASKS_COUNT = 128
PROXY_QUEUE_SIZE = 512

MIN_PROXY_CHECKING_PERIOD = 5 * 60
MAX_PROXY_CHECKING_PERIOD = 45 * 60
BAD_PROXY_CHECKING_PERIOD = 2 * 60 * 60
DEAD_PROXY_CHECKING_PERIOD = 24 * 60 * 60
DEAD_PROXY_THRESHOLD = 6
REMOVE_ON_N_BAD_CHECKS = DEAD_PROXY_THRESHOLD + 21
PROXY_CHECKING_TIMEOUT = 20

PROXY_PROVIDER_SERVER_ADDRESS = {
    'HOST': 'localhost',
    'PORT': 55555,
}

_PROXY_PROVIDER_SERVER_API_CONFIG_FETCH_CONFIG = {
    'fields': ['address', 'protocol', 'auth_data', 'domain', 'port', 'last_check_time',
               'number_of_bad_checks', 'bad_proxy', 'uptime', 'response_time'],
    'filter_fields': ['last_check_time', 'protocol', 'number_of_bad_checks', 'bad_proxy', 'uptime',
                      'response_time'],
    'order_by_fields': ['last_check_time', 'number_of_bad_checks', 'uptime', 'response_time'],
    'default_order_by_fields': ['response_time', ],
}

PROXY_PROVIDER_SERVER_API_CONFIG = {
    'proxy': {
        'model_class': ('models', 'Proxy'),
        'methods': {
            'get': _PROXY_PROVIDER_SERVER_API_CONFIG_FETCH_CONFIG,
            'count': _PROXY_PROVIDER_SERVER_API_CONFIG_FETCH_CONFIG,
        }
    }
}
