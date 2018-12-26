import re

from peewee import RawQuery

from models import Proxy, db
from proxy_py import settings
from server.api_v1.requests_to_models.request_parser import ParseError
from server.base_app import BaseApp

import aiohttp


class ApiRequestHandler:
    def __init__(self, app: BaseApp):
        self.app = app
        self.methods = {
            'get_model': self.get_model,
            'get_proxies_for_id': self.get_proxies_for_id,
            'get_proxy_for_id': self.get_proxy_for_id,
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
        # TODO: implement
        validate_dict_must_have_key(data, 'name')

        model_name = data['name']
        validate_letters_digits_undescores(model_name)
        if model_name not in settings.PROXY_PROVIDER_SERVER_API_CONFIG:
            raise ParseError("You're not allowed to see this model")


        return {
            "result": "model " + model_name,
        }

    async def get_proxy_for_id(self, data: dict) -> dict:
        data['number'] = 1
        res = await self.get_proxies_for_id(data)
        res["result"] = res["results"][0]
        del res["results"]
        del res["number_of_results"]
        return res

    async def get_proxies_for_id(self, data: dict) -> dict:
        validate_dict_must_have_key(data, 'id')
        validate_dict_must_have_key(data, 'number')
        number = int(data['number'])
        validate_uint(number)

        # TODO: validate id
        results = []

        for item in await db.execute(Proxy.raw(
                f'SELECT * FROM working_proxies TABLESAMPLE SYSTEM_ROWS({number});'
        )):
            obj = {}

            for field_name in settings.PROXY_PROVIDER_SERVER_API_CONFIG_FETCH_CONFIG['fields']:
                obj[field_name] = getattr(item, field_name)

            results.append(obj)

        return {
            "number_of_results": len(results),
            "results": results,
        }


def validate_dict_must_have_key(data: dict, key: str):
    if key not in data:
        raise ParseError(f'please, specify the "{key}" key')


def validate_letters_digits_undescores(value):
    if len(value) > settings.PROXY_PROVIDER_SERVER_MAXIMUM_STRING_FIELD_SIZE:
        raise ParseError(f'value "{value}" is too big')

    return validate_regex(value, r'^[a-zA-Z0-9_]+$')


def validate_regex(value: str, regex: str):
    if type(value) is not str:
        raise ParseError(f'value "{value}" should be string')

    if not re.match(regex, value):
        raise ParseError(f"value \"{value}\" doesn't match to regex \"{regex}\"")


def validate_uint(value):
    if type(value) is not int:
        raise ParseError("value should be integer")
    if value < 0:
        raise ParseError("value should be positive")
