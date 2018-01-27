
class Request:
    def __init__(self, class_name):
        self.class_name = class_name


class GetRequest(Request):
    def __init__(self, class_name, fields: list=None):
        super(GetRequest, self).__init__(class_name)
        self.fields = fields if fields is not None else []

    @staticmethod
    def from_request(request: Request):
        return GetRequest(request.class_name)
