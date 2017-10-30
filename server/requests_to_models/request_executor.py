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

        # TODO: remove bad_proxy
        queryset = Class.objects.filter(bad_proxy=False)
        result = []

        for item in queryset:
            obj = {}

            for field_name in request['fields']:
                obj[field_name] = getattr(item, field_name)

            result.append(obj)

        return {
            'data': result,
            'count': Class.objects.count(),
            'last_page': True,
        }


class ExecutionError(Exception):
    pass