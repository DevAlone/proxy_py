import aiohttp

import settings
from server.base_app import BaseApp
from .requests_to_models.request_parser import RequestParser, ParseError
from .requests_to_models.request_executor import RequestExecutor, ExecutionError


class ApiRequestHandler:
    def __init__(self, app: BaseApp):
        self.request_parser = RequestParser(settings.server.api_config)
        self.request_executor = RequestExecutor()
        self.app = app

    async def handle(self, request: aiohttp.ClientRequest, post_data: dict):
        try:
            req_dict = self.request_parser.parse(post_data)

            response = {
                'status': 'ok',
            }
            response.update(await self.request_executor.execute(req_dict))
        except ParseError as ex:
            self.app.log_info(
                request,
                "Error during parsing request. Request: {} Exception: {}".format(
                    post_data,
                    ex
                )
            )

            response = {
                'status': 'error',
                'status_code': 400,
                'error_message': str(ex)
            }
        except ExecutionError as ex:
            self.app.log_error(
                request,
                "Error during execution request. Request: {} Exception: {}".format(
                    post_data,
                    ex
                )
            )
            self.app.log_exception(request, ex)

            response = {
                'status': 'error',
                'status_code': 500,
                'error_message': 'error during execution request'
            }

        return response
