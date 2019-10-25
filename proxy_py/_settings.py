from checkers.google_com_checker import GoogleComChecker


# enable to get more information in logs
DEBUG = False

"""
Database settings (do not try to change after creation of the database)
"""
GEOLITE2_CITY_FILE_LOCATION = '/tmp/proxy_py_9910549a_7d41_4102_9e9d_15d39418a5cb/GeoLite2-City.mmdb'

DATABASE_CONNECTION_ARGS = ()
DATABASE_CONNECTION_KWARGS = {
    'database': 'proxy_py',
    'user': 'proxy_py',
    'password': 'proxy_py',
    'max_connections': 20,
}

DB_MAX_DOMAIN_LENGTH = 128
DB_AUTH_DATA_MAX_LENGTH = 64

"""
Fetcher settings
"""

# it allows you to override or add your own collectors
# for example if you're making proxy checker for particular site
# you can override COLLECTORS_DIR and PROXY_CHECKERS
COLLECTORS_DIRS = [
    'collectors',
    # 'local/collectors',  # use to add your own collectors
]

NUMBER_OF_CONCURRENT_TASKS = 128
# makes aiohttp to not send more
# than this number of simultaneous requests
# works by common connector
NUMBER_OF_SIMULTANEOUS_REQUESTS = 128
# the same, but per host
NUMBER_OF_SIMULTANEOUS_REQUESTS_PER_HOST = NUMBER_OF_SIMULTANEOUS_REQUESTS

MIN_PROXY_CHECKING_PERIOD = 10 * 60
MAX_PROXY_CHECKING_PERIOD = 30 * 60
BAD_PROXY_CHECKING_PERIOD = MAX_PROXY_CHECKING_PERIOD * 2
DEAD_PROXY_THRESHOLD = 12
DEAD_PROXY_CHECKING_PERIOD = 1 * 24 * 60 * 60
DO_NOT_CHECK_ON_N_BAD_CHECKS = DEAD_PROXY_THRESHOLD + 14
# how many seconds to wait for response from proxy
PROXY_CHECKING_TIMEOUT = 10
# do not check proxy from collector if it has been checked recently
PROXY_NOT_CHECKING_PERIOD = 15 * 60
# limiter for maximum number of proxies gotten from collector
# to fix potential issue with collectors' spamming
COLLECTOR_MAXIMUM_NUMBER_OF_PROXIES_PER_REQUEST = 16384
SLEEP_AFTER_ERROR_PERIOD = 10
# how many collectors to process concurrently
NUMBER_OF_CONCURRENT_COLLECTORS = 1

# how many checkers should say that proxy is working
# to consider it so
# should be in range from 1 to len(PROXY_CHECKERS)
# Note: the order of the checkers won't be the same,
# they're shuffled for each proxy
MINIMUM_NUMBER_OF_CHECKERS_PER_PROXY = 1

PROXY_CHECKERS = [
    GoogleComChecker,
]

"""
Server settings
"""

PROXY_PROVIDER_SERVER_ADDRESS = {
    'HOST': 'localhost',
    'PORT': 55555,
}

PROXY_PROVIDER_SERVER_MAXIMUM_REQUEST_LENGTH = 1024
PROXY_PROVIDER_SERVER_MAXIMUM_STRING_FIELD_SIZE = 128

PROXY_PROVIDER_SERVER_API_CONFIG_FETCH_CONFIG = {
    'fields': [
        'address', 'protocol', 'auth_data', 'domain', 'port', 'last_check_time', 'next_check_time', 'number_of_bad_checks',
        'bad_proxy', 'uptime', 'response_time', 'white_ipv4', 'white_ipv6', 'location'
    ],
    'filter_fields': [
        'last_check_time', 'protocol', 'number_of_bad_checks', 'bad_proxy', 'uptime', 'response_time'
    ],
    'order_by_fields': ['last_check_time', 'number_of_bad_checks', 'uptime', 'response_time', 'country_code'],
    'default_order_by_fields': ['response_time', ],
}

PROXY_PROVIDER_SERVER_API_CONFIG = {
    'proxy': {
        'model_class': ['models', 'Proxy'],
        'methods': {
            'get': PROXY_PROVIDER_SERVER_API_CONFIG_FETCH_CONFIG,
            'count': PROXY_PROVIDER_SERVER_API_CONFIG_FETCH_CONFIG,
        }
    }
}

TEMPLATES_PATH = "server/templates"
