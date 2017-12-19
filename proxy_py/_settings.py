import os

DATABASE_CONNECTION_ARGS = (
    'sqlite:///db.sqlite3',
)

DATABASE_CONNECTION_KWARGS = {}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# fetcher settings

PROXY_CHECKING_PERIOD = 10 * 60
BAD_PROXY_CHECKING_PERIOD = 60 * 60
REMOVE_ON_N_BAD_CHECKS = 500

PROXY_PROVIDER_SERVER_ADDRESS = {
    'HOST': 'localhost',
    'PORT': 55555,
}

PROXY_PROVIDER_SERVER_API_CONFIG = {
    'proxy': {
        'modelClass': ('models', 'Proxy'),
        'methods': {
            'get': {
                'fields': ['address', 'protocol', 'auth_data', 'domain', 'port', 'last_check_time',
                           'number_of_bad_checks', 'bad_proxy', 'uptime', 'response_time'],
                'filterFields': ['last_check_time', 'protocol', 'number_of_bad_checks', 'bad_proxy', 'uptime',
                                 'response_time'],
                'orderFields': ['last_check_time', 'number_of_bad_checks', 'uptime'],
            }
        }
    }
}
