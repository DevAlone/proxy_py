from proxy_py import settings
from models import db, Proxy, ProxyCountItem, CollectorState
from server.base_app import BaseApp
from aiohttp import web

import time
import datetime
import functools
import aiohttp_jinja2


def get_response_wrapper(template_name):
    def decorator_wrapper(func):
        @functools.wraps(func)
        @aiohttp_jinja2.template(template_name)
        async def wrap(self, *args, **kwargs):
            good_proxies_count = await db.count(
                Proxy.select().where(Proxy.number_of_bad_checks == 0)
            )

            bad_proxies_count = await db.count(
                Proxy.select().where(
                    Proxy.number_of_bad_checks > 0,
                    Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD,
                )
            )

            dead_proxies_count = await db.count(
                Proxy.select().where(
                    Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD,
                )
            )

            response = {
                "bad_proxies_count": bad_proxies_count,
                "good_proxies_count": good_proxies_count,
                "dead_proxies_count": dead_proxies_count,
            }

            response.update(await func(self, *args, **kwargs))

            return response
        return wrap

    return decorator_wrapper


class App(BaseApp):
    async def setup_router(self):
        self.app.router.add_get('/get/proxy/', self.get_proxies_html)
        self.app.router.add_get('/get/proxy_count_item/', self.get_proxy_count_items_html)
        self.app.router.add_get('/get/collector_state/', self.get_collector_state_html)
        self.app.router.add_get('/get/best/http/proxy/', self.get_best_http_proxy)

    @get_response_wrapper("collector_state.html")
    async def get_collector_state_html(self, request):
        return {
            "collector_states": list(await db.execute(CollectorState.select())),
        }

    @get_response_wrapper("proxies.html")
    async def get_proxies_html(self, request):
        proxies = await db.execute(
            Proxy.select().where(Proxy.number_of_bad_checks == 0).order_by(Proxy.response_time)
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
                "city": proxy.city,
                "region": proxy.region,
                "country_code": proxy.country_code,
            } for proxy in proxies]
        }

    @get_response_wrapper("proxy_count_items.html")
    async def get_proxy_count_items_html(self, request):
        return {
            "proxy_count_items": list(await db.execute(ProxyCountItem.select().order_by(ProxyCountItem.timestamp)))
        }

    async def get_best_http_proxy(self, request):
        proxy_address = (await db.get(
            Proxy.select().where(
                Proxy.number_of_bad_checks == 0,
                Proxy.raw_protocol == Proxy.PROTOCOLS.index("http"),
            ).order_by(Proxy.response_time)
        )).address

        return web.Response(text=proxy_address)
