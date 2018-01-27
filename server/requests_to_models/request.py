
class Request:
    def __init__(self, class_name):
        self.class_name = class_name


class FetchRequest(Request):
    def __init__(self, class_name, fields: list=None, order_by: list=None):
        super(FetchRequest, self).__init__(class_name)
        self.fields = fields if fields is not None else []
        self.order_by = order_by if order_by is not None else []
        self.limit = 0
        self.offset = 0


class GetRequest(FetchRequest):
    @staticmethod
    def from_request(request: Request):
        return GetRequest(request.class_name)


class CountRequest(FetchRequest):
    @staticmethod
    def from_request(request: Request):
        return CountRequest(request.class_name)
