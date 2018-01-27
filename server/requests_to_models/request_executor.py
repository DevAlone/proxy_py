from models import session
from server.requests_to_models.request import Request, GetRequest
import importlib


class RequestExecutor:
    def execute(self, request: Request):
        try:
            return {
                GetRequest: self._get,
            }[type(request)](request)
        except BaseException as ex:
            raise ExecutionError(repr(ex))

    def _get(self, request: GetRequest):
        package = importlib.import_module(request.class_name[0])
        class_name = getattr(package, request.class_name[1])

        # TODO: remove bad_proxy

        queryset = session.query(class_name).filter(class_name.number_of_bad_checks == 0)
        result = []

        for item in queryset:
            obj = {}

            for field_name in request.fields:
                obj[field_name] = getattr(item, field_name)

            result.append(obj)

        return {
            'data': result,
            'count': queryset.count(),
            'has_more': False,
        }


class ExecutionError(Exception):
    pass
