from proxy_py import settings
from models import session
from server.requests_to_models.request import Request, GetRequest, CountRequest, FetchRequest
import importlib


class RequestExecutor:
    def execute(self, request: Request):
        try:
            if isinstance(request, FetchRequest):
                return self._fetch(request)
            # return {
            #     # GetRequest: self._get,
            #     # CountRequest: self._count
            #     FetchRequest: self._fetch
            # }[type(request)](request)
        except BaseException as ex:
            raise ExecutionError(repr(ex))

    def _fetch(self, request: FetchRequest):
        package = importlib.import_module(request.class_name[0])
        class_name = getattr(package, request.class_name[1])

        # TODO: remove checking number_of_bad_checks

        queryset = session.query(class_name).filter(class_name.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD)

        result = {
            'count': queryset.count(),
        }

        if type(request) is GetRequest:
            if request.order_by:
                queryset = queryset.order_by(*self.order_by_list_to_sqlalchemy(request.order_by, class_name))

            if request.limit > 0:
                queryset = queryset.limit(request.limit)

            if request.offset > 0:
                queryset = queryset.offset(request.offset)

            data = []

            for item in queryset:
                obj = {}

                for field_name in request.fields:
                    obj[field_name] = getattr(item, field_name)

                data.append(obj)

            result['data'] = data
            result['has_more'] = request.offset + request.limit < result['count']

        return result

    def order_by_list_to_sqlalchemy(self, order_by_fields: list, class_name):
        result = []
        for field in order_by_fields:
            reverse = False
            if field[0] == '-':
                reverse = True
                field = field[1:]

            attribute = getattr(class_name, field)
            if reverse:
                attribute = attribute.desc()

            result.append(attribute)

        return result


class ExecutionError(Exception):
    pass
