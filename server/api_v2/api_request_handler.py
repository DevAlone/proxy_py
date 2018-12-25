import re

from proxy_py import settings
from server.api_v1.requests_to_models.request_parser import ParseError
from server.base_app import BaseApp

import aiohttp


class ApiRequestHandler:
    def __init__(self, app: BaseApp):
        self.app = app
        self.methods = {
            'get_model': self.get_model,
        }

    async def handle(self, request: aiohttp.ClientRequest, method_name: str, post_data: dict):
        try:
            response = {
                'status': 'ok',
            }
            if method_name not in self.methods:
                response = {
                    'status': 'error',
                    'status_code':400,
                    'error_message': "there is no any method with this name",
                }
            else:
                response.update(await self.methods[method_name](post_data))
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
        except ValueError as ex:
            response = {
                'status': 'error',
                'status_code':400,
                'error_message': "something's wrong with your request",
            }
            self.app.log_error(
                request,
                f'ValueError: {ex}'
            )
        except BaseException as ex:
            response = {
                'status': 'error',
                'status_code': 500,
                'error_message': 'something bad happened, call the admin',
            }
            self.app.log_error(
                request,
                f'Error during execution request. Method: {method_name}. Request: {request}. Exception: {ex}'
            )
        # except ExecutionError as ex:
        #     self.app.log_error(
        #         request,
        #         "Error during execution request. Request: {} Exception: {}".format(
        #             post_data,
        #             ex
        #         )
        #     )
        #
        #     response = {
        #         'status': 'error',
        #         'status_code': 500,
        #         'error_message': 'error during execution request'
        #     }

        return response

    async def get_model(self, data: dict) -> dict:
        if 'name' not in data:
            raise ParseError('please, specify the "name" key')

        model_name = data['name']
        validate_letters_digits_undescores(model_name)
        if model_name not in settings.PROXY_PROVIDER_SERVER_API_CONFIG:
            raise ParseError("You're not allowed to see this model")


        return {
            "result": "model " + model_name,
        }


def validate_letters_digits_undescores(value):
    if len(value) > settings.PROXY_PROVIDER_SERVER_MAXIMUM_STRING_FIELD_SIZE:
        raise ParseError(f'value "{value}" is too big')

    return validate_regex(value, r'^[a-zA-Z0-9_]+$')


def validate_regex(value: str, regex: str):
    if type(value) is not str:
        raise ParseError(f'value "{value}" should be string')

    if not re.match(regex, value):
        raise ParseError(f"value \"{value}\" doesn't match to regex \"{regex}\"")
