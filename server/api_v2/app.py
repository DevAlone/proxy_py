import json

import aiohttp

from proxy_py import settings
from server.base_app import BaseApp

from .api_request_handler import ApiRequestHandler


class App(BaseApp):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.request_handler = ApiRequestHandler(self)

    async def setup_router(self):
        self.app.router.add_post("/{method_name:[a-z_0-9]+}", self.post)

    async def post(self, request):
        method_name = request.match_info["method_name"]
        if method_name is None or not method_name:
            status_code = 400
            response = {
                "status": "error",
                "status_code": 400,
                "error_message": "bad method name",
            }
        else:
            data = await request.read()

            try:
                data = data.decode()
                if len(data) > settings.PROXY_PROVIDER_SERVER_MAXIMUM_REQUEST_LENGTH:
                    response = {
                        "status": "error",
                        "status_code": 400,
                        "error_message": "your request is too fat!",
                    }
                else:
                    data = json.loads(data)

                    response = await self.request_handler.handle(
                        request, method_name, data
                    )
            except ValueError:
                response = {
                    "status": "error",
                    "status_code": 400,
                    "error_message": "your request doesn't look like request",
                }

            if "status_code" in response:
                status_code = response["status_code"]
            else:
                if response["status"] != "ok":
                    status_code = 500
                else:
                    status_code = 200

                response["status_code"] = status_code

        return aiohttp.web.json_response(response, status=status_code)
