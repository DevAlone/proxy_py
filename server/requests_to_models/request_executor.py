import importlib

class RequestExecutor:
    def execute(self, request):
        try:
            return {
                'get': self._get,
            }[request['method']](request)
        except Exception as ex:
            raise ExecutionError(repr(ex))
        except:
            raise ExecutionError()

    def _get(self, request):
        Package = importlib.import_module(request['ClassName'][0])
        Class = getattr(Package, request['ClassName'][1])

        queryset = Class.objects.all()
        result = []

        for item in queryset:
            obj = {}

            for fieldName in request['fields']:
                obj[fieldName] = getattr(item, fieldName)
            result.append(obj)

        return result


class ExecutionError(Exception):
    pass