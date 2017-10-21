# TODO: limit user's input
# TODO: limit items to process

import string
import copy

import re


class RequestParser:
    ALLOWED_CHARS = string.ascii_letters + string.digits + "/: !=><,-*"
    MAXIMUM_STRING_REQUEST_LENGTH = 128
    COMMA_SEPARATED_KEYS = ["fields", "order_by"]
    ALLOWED_KEYS = ['model', 'method', 'fields', 'order_by']

    def __init__(self, config):
        self.config = config
        self._validateConfig()

    # input is string
    def parse(self, request):
        if len(request) > self.MAXIMUM_STRING_REQUEST_LENGTH:
            raise ParseError("Your're request is too long. Maximum request is {} symbols"
                             .format(self.MAXIMUM_STRING_REQUEST_LENGTH))

        request = self._keepAllowedChars(request)

        items = [item for item in request.split('/') if item]

        reqDict = {}
        for item in items:
            keyVal = item.split(':')
            keyVal[0] = keyVal[0].strip()
            keyVal[1] = keyVal[1].strip()
            if keyVal[0] in self.COMMA_SEPARATED_KEYS:
                keyVal[1] = self._commaSeparatedFieldToList(keyVal[1])
                if not len(keyVal[1]):
                    continue
            self._validateField(*keyVal)

            reqDict[keyVal[0]] = keyVal[1]

        return self._parseDict(reqDict)

    def _validateField(self, key, value):
        if key not in self.ALLOWED_KEYS:
            raise ValidationError("key {} isn't allowed".format(key))

        if type(value) is list:
            for valueItem in value:
                self._validateField(key, valueItem)
            return

        # TODO: complete that
        if key in ['method', 'model', 'fields']:
            if not re.match(r'^[a-zA-Z0-9_*]+$', value):
                raise ValidationError("'{}' value doesn't match to pattern ^[a-zA-Z0-9_]+$".format(key))

    def _commaSeparatedFieldToList(self, stringField):
        return [val.strip() for val in stringField.split(',') if val]

    def _keepAllowedChars(self, request):
        request = request.strip()
        res = ""
        for ch in request:
            if ch == ' ' and res[-1] == ch:
                continue

            if ch in self.ALLOWED_CHARS:
                res += ch

        return res

    def _parseDict(self, reqDict):
        self.resultRequest = {}
        if 'model' not in reqDict:
            raise ParseError("You should specify 'model'")

        if reqDict['model'] not in self.config:
            raise  ParseError("Model doesn't exist or isn't allowed")

        config = self.config[reqDict['model']]

        self.resultRequest['ClassName'] = config['modelClass']

        if 'method' not in reqDict:
            raise ParseError("You should specify 'method'")

        if reqDict['method'] not in config['methods']:
            raise ParseError("Method doesn't exist or isn't allowed")

        self.resultRequest['method'] = reqDict['method']

        config = config['methods'][reqDict['method']]
        return {
            'get': self._get,
        }[reqDict['method']](reqDict, config)

    def _get(self, reqDict, config):
        if 'fields' not in reqDict:
            reqDict['fields'] = ["*"]

        self.resultRequest['fields'] = []

        if len(reqDict['fields']) == 1 and reqDict['fields'][0] == '*':
            self.resultRequest['fields'] = copy.copy(config['fields'])
        else:
            for field in reqDict['fields']:
                if field not in config['fields']:
                    raise ParseError("Field '{}' doesn't exist or isn't allowed".format(field))
                self.resultRequest['fields'].append(field)

        return self.resultRequest

    def _validateConfig(self):
        if False:
            raise ConfigFormatError()


class ParseError(Exception):
    pass

class ValidationError(ParseError):
    pass


class ConfigFormatError(Exception):
    pass