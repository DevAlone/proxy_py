from requests_to_models.request_parser import RequestParser
from requests_to_models.request_executor import RequestExecutor

import init_django

from core.models import Proxy

if __name__ == '__main__':
    config = {
        'proxy': {
            'modelClass': Proxy,
            'methods': {
                'get': {
                    'fields': ['address', 'whiteIp', 'lastCheckedTime', 'numberOfBadChecks', 'badProxy', 'uptime'],
                    'filterFields': ['whiteIp', 'lastCheckedTime', 'numberOfBadChecks', 'badProxy', 'uptime'],
                    'orderFields': ['lastCheckedTime', 'numberOfBadChecks', 'uptime'],
                }
            }
        }
    }


    parser = RequestParser(config)

    req = parser.parse(" /model :proxy/method:get/filter:  bad   Proxy != False/fields:*")

    print(req)
    print()

    executor = RequestExecutor()
    data = executor.execute(req)
    print(data)
