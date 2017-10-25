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
    def handle(self, client_address, http_method, headers, post_data):
        try:
            if http_method == 'get':
                return self.index()

            # strRequest = urllib.parse.unquote(res.groups()[1])

            try:
                json_data = json.loads(post_data)
            except:
                raise ParseError("Your request doesn't look like json. Maybe it's not json?")

            reqDict = self.requestParser.parse(json_data)

            response = {
                'status': 'ok',
                'data': self.requestExecutor.execute(reqDict)
            }
        except ParseError as ex:
            self._logger.warning(
                "Error during parsing request. \nClient: {} \nRequest: {} \nException: {}".format(
                    client_address,
                    (http_method, headers, post_data),
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
                    (http_method, headers, post_data),
                    ex)
            )

            response = {
                'status': 'error',
                'error': 'error during execution request'
            }
        except:
            self._logger.exception("Error in ApiRequestHandler. \nClient: {} \nRequest: {}".format(
                    client_address,
                    (http_method, headers, post_data))
            )

            response = {
                'status': 'error',
                'error': 'Something very bad happened'
            }

        return self.make_http_response(json.dumps(response).encode('utf-8'))

    def index(self):
        return b"""HTTP/1.1 200 OK
Server: Apache/1.3.37
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>title</title>
<style>
html, body {
    width: 100%;
    height: 100%;
    background: #eee;
    padding: 0;
    margin: 0;
    line-height: 0;
}
</style>
</head>
<body>

<iframe width="100%" height="100%" src="https://www.youtube.com/embed/7OBx-YwPl8g?rel=0&autoplay=1" frameborder="0" allowfullscreen></iframe>
</body>

</html> 
"""

    def make_http_response(self, bytesData):
        HTTP_HEADER = b"""HTTP/1.1 200 OK
Server: Apache/1.3.37
Content-Type: application/json; charset=utf-8

"""
        return HTTP_HEADER + bytesData