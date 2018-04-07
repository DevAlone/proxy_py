from server.base_app import BaseApp
from .api_request_handler import ApiRequestHandler
from aiohttp import web

import json
import aiohttp


class App(BaseApp):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.request_handler = ApiRequestHandler(self)

    async def setup_router(self):
        self.app.router.add_post('/', self.post)

    async def post(self, request):
        client_address = request.transport.get_extra_info('peername')
        host, port = (None, None)

        if client_address is not None:
            host, port = client_address
        else:
            client_address = (host, port)

        data = await request.read()

        with open("logs/apiv1_server_connections", 'a') as f:
            f.write("client - {}:{}, data - {}\n".format(host, port, data))

        try:
            data = json.loads(data.decode())

            response = await self.request_handler.handle(request, data)
        except ValueError:
            response = {
                'status': 'error',
                'status_code': 400,
                'error_message': "Your request doesn't look like request",
            }

        if 'status_code' in response:
            status_code = response['status_code']
        else:
            if response['status'] != 'ok':
                status_code = 500
            else:
                status_code = 200

            response['status_code'] = status_code

        return aiohttp.web.json_response(response, status=status_code)
