from server.requests_to_models.request import Request, GetRequest

import string
import copy
import re


class RequestParser:
    ALLOWED_CHARS = string.ascii_letters + string.digits + "/: !=><,-*"
    COMMA_SEPARATED_KEYS = {"fields", "order_by"}
    ALLOWED_KEYS = {'model', 'method', 'fields', 'filter', 'order_by', 'limit', 'offset'}
    MAXIMUM_KEY_LENGTH = 64
    MAXIMUM_VALUE_LENGTH = 512

    def __init__(self, config):
        self.config = config
        self._validate_config()

    def parse(self, request: dict):
        for key in request.keys():
            request[key] = str(request[key])
            self.validate_key(key)

            if key in self.COMMA_SEPARATED_KEYS:
                request[key] = self.comma_separated_field_to_list(request[key])

            self.validate_value(key, request[key])

        return self.parse_dict(request)

    def validate_value(self, key: str, value):
        if type(value) not in [str, int, list]:
            raise ValidationError('Value type should be string, integer or list')

        if len(value) > self.MAXIMUM_VALUE_LENGTH:
            raise ValidationError(
                'Some value is too big. Maximum allowed length is {}'.format(self.MAXIMUM_VALUE_LENGTH))

        # validate list types
        if type(value) is list:
            for value_item in value:
                self.validate_value(key, value_item)
            return

        if key in {'model', 'method', 'fields', 'order_by'}:
            self._validate_value_type(key, value, str)
            self._validate_value_regex(key, value, r'^[a-zA-Z][a-zA-Z0-9_]+$')
        elif key in {'filter'}:
            self._validate_value_type(key, value, str)
            self._validate_value_regex(key, value, r'^[a-zA-Z0-9_]+$')
        elif key in {'limit', 'offset'}:
            self._validate_value_type(key, value, int)
            if value < 0:
                raise ValidationError('Value of key "{}" should be positive'.format(key))
        else:
            # It means I forget to add validation of field
            raise ValidationError('Server Error')

    def _validate_value_regex(self, key, value, pattern):
        if not re.match(pattern, value):
            raise ValidationError("Value of key '{}' doesn't match to pattern {}".format(key, pattern))

    def _validate_value_type(self, key, value, type):
        if type(value) is not type:
            raise ValidationError('Value of key "{}" should be {}'.format(key, type))

    def validate_key(self, key: str):
        if type(key) is not str:
            raise ValidationError("Key {} is not string".format(key))
        if len(key) > self.MAXIMUM_KEY_LENGTH:
            raise ValidationError(
                'Some key is too big. Maximum allowed length is {}'.format(key, self.MAXIMUM_KEY_LENGTH))
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]+$', key):
            raise ValidationError('Key "{}" doesn\'t match to pattern ^[a-zA-Z][a-zA-Z0-9_]+$'.format(key))
        if key not in self.ALLOWED_KEYS:
            raise ValidationError('Key "{}" isn\'t allowed'.format(key))

    def comma_separated_field_to_list(self, string_field):
        result = []
        for val in string_field.split(','):
            val = val.strip()
            if val:
                result.append(val)
        return result

    def parse_dict(self, req_dict):
        if 'model' not in req_dict:
            raise ParseError('You should specify "model"')

        if req_dict['model'] not in self.config:
            raise ParseError("Model doesn't exist or isn't allowed")

        config = self.config[req_dict['model']]

        result_request = Request(config['modelClass'])

        if 'method' not in req_dict:
            raise ParseError('You should specify "method"')

        method = req_dict['method']

        if method not in config['methods']:
            raise ParseError("Method doesn't exist or isn't allowed")

        config = config['methods'][method]

        return {
            'get': self._get,
        }[method](req_dict, config, result_request)

    def _get(self, req_dict, config, result_request):
        fields = []

        if 'fields' not in req_dict:
            fields = copy.copy(config['fields'])
        else:
            for field in req_dict['fields']:
                if field not in config['fields']:
                    raise ParseError("Field \"{}\" doesn't exist or isn't allowed".format(field))

                fields.append(field)

        result_request = GetRequest.from_request(result_request)
        result_request.fields = fields

        return result_request

    def _validate_config(self):
        # TODO: check fields for existence and so on
        if False:
            raise ConfigFormatError()


class ParseError(Exception):
    pass


class ValidationError(ParseError):
    pass


class ConfigFormatError(Exception):
    pass
