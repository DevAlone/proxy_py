# TODO: limit user's input
# TODO: limit items to process

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

    def parse(self, request : dict):
        for key in request.keys():
            request[key] = str(request[key])
            if key in self.COMMA_SEPARATED_KEYS:
                request[key] = self._comma_separated_field_to_list(request[key])
            self._validate_key_value(key, request[key])

        return self._parseDict(request)

    def _validate_key_value(self, key, value):
        self._validate_key(key)

        if len(key) > self.MAXIMUM_KEY_LENGTH:
            raise ValidationError(
                'Some key is too big. Maximum allowed length is {}'.format(self.MAXIMUM_KEY_LENGTH))
        if len(value) > self.MAXIMUM_VALUE_LENGTH:
            raise ValidationError(
                'Some value is too big. Maximum allowed length is {}'.format(self.MAXIMUM_VALUE_LENGTH))

        # validate list types
        if type(value) is list:
            for value_item in value:
                self._validate_key_value(key, value_item)
            return

        if key in {'model', 'method', 'fields', 'order_by'}:
            self._validate_value_regex(key, value, r'^[a-zA-Z][a-zA-Z0-9_]+$')
        elif key in {'filter'}:
            self._validate_value_regex(key, value, r'^[a-zA-Z0-9_]+$')
            pass
        elif key in {'limit', 'offset'}:
            if type(value) is not int:
                raise ValidationError("Value of key '{}' should be int".format(key))
            pass
        else:
            # It means I forget to add validation of field
            raise ValidationError('Server Error')

    def _validate_value_regex(self, key, value, pattern):
        if not re.match(pattern, value):
            raise ValidationError("Value of key '{}' doesn't match to pattern {}".format(key, pattern))

    def _validate_key(self, key):
        if type(key) is not str:
            raise ValidationError("Key {} is not string".format(key))
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]+$', key):
            raise ValidationError("Key '{}' doesn't match to pattern ^[a-zA-Z][a-zA-Z0-9_]+$".format(key))
        if key not in self.ALLOWED_KEYS:
            raise ValidationError("Key '{}' isn't allowed".format(key))

    def _comma_separated_field_to_list(self, stringField):
        result = []
        for val in stringField.split(','):
            val = val.strip()
            if val:
                result.append(val)
        return result

    def _parseDict(self, req_dict):
        self.result_request = {}
        if 'model' not in req_dict:
            raise ParseError("You should specify 'model'")

        if req_dict['model'] not in self.config:
            raise  ParseError("Model doesn't exist or isn't allowed")

        config = self.config[req_dict['model']]

        self.result_request['ClassName'] = config['modelClass']

        if 'method' not in req_dict:
            raise ParseError("You should specify 'method'")

        if req_dict['method'] not in config['methods']:
            raise ParseError("Method doesn't exist or isn't allowed")

        self.result_request['method'] = req_dict['method']

        config = config['methods'][req_dict['method']]
        return {
            'get': self._get,
        }[req_dict['method']](req_dict, config)

    def _get(self, req_dict, config):
        if 'fields' not in req_dict:
            req_dict['fields'] = ["*"]
            self.result_request['fields'] = copy.copy(config['fields'])
        else:
            self.result_request['fields'] = []

            for field in req_dict['fields']:
                if field not in config['fields']:
                    raise ParseError("Field '{}' doesn't exist or isn't allowed".format(field))
                self.result_request['fields'].append(field)

        return self.result_request

    def _validate_config(self):
        if False:
            raise ConfigFormatError()


class ParseError(Exception):
    pass


class ValidationError(ParseError):
    pass


class ConfigFormatError(Exception):
    pass