"""
Default settings for package server
"""

hostname = "0.0.0.0"
port = 55555

templates_path = "server/templates"

maximum_request_length = 1024
maximum_string_field_size = 128

api_config_fetch_config = {
    'fields': [
        'address', 'protocol', 'auth_data', 'domain', 'port',
        'last_check_time', 'next_check_time',
        'number_of_bad_checks', 'bad_proxy', 'uptime',
        'response_time', 'white_ipv4', 'white_ipv6', 'location',
    ],
    'filter_fields': [
        'last_check_time', 'protocol', 'number_of_bad_checks', 'bad_proxy',
        'uptime', 'response_time'
    ],
    'order_by_fields': [
        'last_check_time', 'number_of_bad_checks', 'uptime', 'response_time',
    ],
    'default_order_by_fields': ['response_time', ],
}

api_config = {
    'proxy': {
        'model_class': ['storage.models', 'Proxy'],
        'methods': {
            'get': api_config_fetch_config,
            'count': api_config_fetch_config,
        }
    }
}
