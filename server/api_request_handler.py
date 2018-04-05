from server.requests_to_models.request_parser import RequestParser, ParseError
from server.requests_to_models.request_executor import RequestExecutor, ExecutionError
from proxy_py import settings


class ApiRequestHandler:
    def __init__(self, logger):
        self.request_parser = RequestParser(settings.PROXY_PROVIDER_SERVER_API_CONFIG)
        self.request_executor = RequestExecutor()
        self._logger = logger

    async def handle(self, client_address: tuple, post_data: dict):
        try:
            req_dict = self.request_parser.parse(post_data)

            response = {
                'status': 'ok',
            }
            response.update(await self.request_executor.execute(req_dict))
        except ParseError as ex:
            self._logger.warning(
                "Error during parsing request. \nClient: {} \nRequest: {} \nException: {}".format(
                    client_address,
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
            self._logger.warning(
                "Error during execution request. \nClient: {} \nRequest: {} \nException: {}".format(
                    client_address,
                    post_data,
                    ex)
            )

            response = {
                'status': 'error',
                'status_code': 500,
                'error_message': 'error during execution request'
            }

        return response
