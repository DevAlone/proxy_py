import time
import datetime
import functools

import aiohttp_jinja2
from aiohttp import web

import settings
import storage
from storage.models import db
from server.base_app import BaseApp


def get_response_wrapper(template_name):
    def decorator_wrapper(func):
        @functools.wraps(func)
        @aiohttp_jinja2.template(template_name)
        async def wrap(self, *args, **kwargs):
            good_proxies_count = await db.count(
                storage.Proxy.select().where(storage.Proxy.number_of_bad_checks == 0)
            )

            bad_proxies_count = await db.count(
                storage.Proxy.select().where(
                    storage.Proxy.number_of_bad_checks > 0,
                    storage.Proxy.number_of_bad_checks < settings.dead_proxy_threshold,
                )
            )

            dead_proxies_count = await db.count(
                storage.Proxy.select().where(
                    storage.Proxy.number_of_bad_checks >= settings.dead_proxy_threshold,
                    storage.Proxy.number_of_bad_checks < settings.do_not_check_on_n_bad_checks,
                )
            )

            not_checked_proxies_count = await db.count(
                storage.Proxy.select().where(
                    storage.Proxy.number_of_bad_checks >= settings.do_not_check_on_n_bad_checks,
                )
            )

            response = {
                "bad_proxies_count": bad_proxies_count,
                "good_proxies_count": good_proxies_count,
                "dead_proxies_count": dead_proxies_count,
                "not_checked_proxies_count": not_checked_proxies_count,
            }

            response.update(await func(self, *args, **kwargs))

            return response

        return wrap

    return decorator_wrapper


class App(BaseApp):
    async def setup_router(self):
        self.app.router.add_get('/get/proxy/', self.get_proxies_html)
        self.app.router.add_get('/get/proxy_count_item/', self.get_proxy_count_items_html)
        self.app.router.add_get('/get/number_of_proxies_to_process/', self.get_number_of_proxies_to_process_html)
        self.app.router.add_get('/get/collector_state/', self.get_collector_state_html)
        self.app.router.add_get('/get/best/http/proxy/', self.get_best_http_proxy)

    #     self.app.router.add_get('/{tail:.*}', self.default_route)
    #
    # async def default_route(self, request: aiohttp.ClientRequest):
    #     path = request.path
    #     if path == '/':
    #         path = '/index.html'
    #
    #     if re.match(r'^(/([a-zA-Z0-9_]+(\.[a-zA-Z0-9]+)*)?)+$', path):
    #         try:
    #             path = os.path.join('./server/frontend/angular/dist', path)
    #             with open(path, 'r'):
    #                 return web.FileResponse(path)
    #         except (FileNotFoundError, IsADirectoryError):
    #             pass
    #
    #     return web.FileResponse('./server/frontend/angular/dist/index.html')

    @get_response_wrapper("collector_state.html")
    async def get_collector_state_html(self, request):
        return {
            "collector_states": list(await db.execute(storage.CollectorState.select())),
        }

    @get_response_wrapper("proxies.html")
    async def get_proxies_html(self, request):
        proxies = await db.execute(
            storage.Proxy.select().where(storage.Proxy.number_of_bad_checks == 0).order_by(storage.Proxy.response_time)
        )
        proxies = list(proxies)
        current_timestamp = time.time()

        return {
            "proxies": [{
                "address": proxy.address,
                "response_time": proxy.response_time / 1000 if proxy.response_time is not None else None,
                "uptime": datetime.timedelta(
                    seconds=int(current_timestamp - proxy.uptime)) if proxy.uptime is not None else None,
                "bad_uptime": datetime.timedelta(
                    seconds=int(current_timestamp - proxy.bad_uptime)) if proxy.bad_uptime is not None else None,
                "last_check_time": proxy.last_check_time,
                "checking_period": proxy.checking_period,
                "number_of_bad_checks": proxy.number_of_bad_checks,
                "bad_proxy": proxy.bad_proxy,
                "white_ipv4": proxy.white_ipv4,
                "location": proxy.location,
            } for proxy in proxies]
        }

    @get_response_wrapper("proxy_count_items.html")
    async def get_proxy_count_items_html(self, request):
        return {
            "proxy_count_items": list(await db.execute(
                storage.ProxyCountItem.select().where(
                    storage.ProxyCountItem.timestamp >= time.time() - 3600 * 24 * 7,
                ).order_by(storage.ProxyCountItem.timestamp)
            ))
        }

    @get_response_wrapper("number_of_proxies_to_process.html")
    async def get_number_of_proxies_to_process_html(self, request):
        return {
            "number_of_proxies_to_process": list(await db.execute(
                storage.NumberOfProxiesToProcess.select().where(
                    storage.NumberOfProxiesToProcess.timestamp >= time.time() - 3600 * 24 * 7,
                ).order_by(storage.NumberOfProxiesToProcess.timestamp)
            ))
        }

    async def get_best_http_proxy(self, request):
        proxy_address = (await db.get(
            storage.Proxy.select().where(
                storage.Proxy.number_of_bad_checks == 0,
                storage.Proxy.raw_protocol == storage.Proxy.PROTOCOLS.index("http"),
            ).order_by(storage.Proxy.response_time)
        )).address

        return web.Response(text=proxy_address)
