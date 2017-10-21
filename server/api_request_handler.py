from server.requests_to_models.request_parser import RequestParser, ParseError
from server.requests_to_models.request_executor import RequestExecutor, ExecutionError
from proxy_py import settings

import re
import json
import urllib.parse

class ApiRequestHandler:
    HTTP_HEADER = """HTTP/1.1 200 OK
Server: Apache/1.3.37
Content-Type: text/html; charset=utf-8

"""

    def __init__(self):
        self.requestParser = RequestParser(settings.PROXY_PROVIDER_SERVER_API_CONFIG)
        self.requestExecutor = RequestExecutor()

    # input is bytes array
    # result is bytes array
    def handle(self, request):
        response = {}
        isRequestHttp = False


        try:
            strRequest = request.decode('utf-8').strip()
            # find request
            maxReqLen = self.requestParser.MAXIMUM_STRING_REQUEST_LENGTH

            if re.search(r'^(get|GET)\s+/\s+(http|HTTP)', strRequest):
                return self.index()

            try:
                res = re.search(r'^(get|GET) (/.{1,' + str(maxReqLen) + '}/) (http|HTTP)', strRequest)
                if res is None:
                    raise ParseError("Your request looks wrong")
                isRequestHttp = True
                strRequest = urllib.parse.unquote(res.groups()[1])
            except:
                res = re.search(r'/.{1,' + str(maxReqLen) + '}/$', strRequest)
                if res is None:
                    raise ParseError("Your request looks wrong")
                if strRequest.startswith('post') or strRequest.startswith('POST'):
                    isRequestHttp = True
                strRequest = res.group()

            reqDict = self.requestParser.parse(strRequest)

            response = {
                'status': 'ok',
                'data': self.requestExecutor.execute(reqDict)
            }
        except ParseError as ex:
            print(repr(ex))
            response = {
                'status': 'error',
                'error': str(ex)
            }
        except ExecutionError as ex:
            print(repr(ex))
            response = {
                'status': 'error',
                'error': 'error during execution request'
            }
        except Exception as ex:
            print(repr(ex))
            # TODO: log it
            raise ex
            response = {
                'status': 'error',
                'error': 'Something bad happened'
            }
        except:
            response = {
                'status': 'error',
                'error': 'Something very bad happened'
            }

        return self.getRequest(isRequestHttp, (json.dumps(response) + '\n').encode('utf-8'))

    def index(self):
        page = self.HTTP_HEADER + """<!DOCTYPE html>
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
        return page.encode('utf-8')

    def getRequest(self, isRequestHttp, bytesData):
        return self.HTTP_HEADER.encode('utf-8') + bytesData if isRequestHttp else bytesData