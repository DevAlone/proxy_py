from server.requests_to_models.request_parser import RequestParser, ParseError
from server.requests_to_models.request_executor import RequestExecutor, ExecutionError
from proxy_py import settings

import re
import json
import urllib.parse

class ApiRequestHandler:

    def __init__(self, logger):
        self.requestParser = RequestParser(settings.PROXY_PROVIDER_SERVER_API_CONFIG)
        self.requestExecutor = RequestExecutor()
        self._logger = logger

    # input is bytes array
    # result is bytes array
    def handle(self, client_address, post_data):
        try:
            reqDict = self.requestParser.parse(post_data)

            response = {
                'status': 'ok',
                'data': self.requestExecutor.execute(reqDict)
            }
        except ParseError as ex:
            self._logger.warning(
                "Error during parsing request. \nClient: {} \nRequest: {} \nException: {}".format(
                    client_address,
                    post_data,
                    ex)
            )

            response = {
                'status': 'error',
                'error': str(ex)
            }
        except ExecutionError as ex:
            self._logger.warning(
                "Error during execution request. \nClient: {} \nRequest: {} \nException: {}".format(
                    client_address,
                    post_data,
                    ex)
            )

            response = {
                'status': 'error',
                'error': 'error during execution request'
            }
        except:
            self._logger.exception("Error in ApiRequestHandler. \nClient: {} \nRequest: {}".format(
                client_address,
                post_data)
            )

            response = {
                'status': 'error',
                'error': 'Something very bad happened'
            }

        return response