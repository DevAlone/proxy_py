import time

import datetime

from server.api_request_handler import ApiRequestHandler
from models import session, Proxy, ProxyCountItem

import aiohttp
import aiohttp.web
import logging


_proxy_provider_server = None
_logger = logging.getLogger('proxy_py/server')
_logger.setLevel(logging.DEBUG)
debug_file_handler = logging.FileHandler('logs/server.debug.log')
debug_file_handler.setLevel(logging.DEBUG)
error_file_handler = logging.FileHandler('logs/server.error.log')
error_file_handler.setLevel(logging.ERROR)
error_file_handler = logging.FileHandler('logs/server.warning.log')
error_file_handler.setLevel(logging.WARNING)
info_file_handler = logging.FileHandler('logs/server.log')
info_file_handler.setLevel(logging.INFO)

_logger.addHandler(debug_file_handler)
_logger.addHandler(error_file_handler)
_logger.addHandler(info_file_handler)

_api_request_handler = ApiRequestHandler(_logger)


class ProxyProviderServer:
    @staticmethod
    def get_proxy_provider_server(host, port, processor):
        global _proxy_provider_server
        if _proxy_provider_server is None:
            _proxy_provider_server = ProxyProviderServer(host, port, processor)
        return _proxy_provider_server

    def __init__(self, host, port, processor):
        self._processor = processor
        self.host = host
        self.port = port

    async def start(self, loop):
        app = aiohttp.web.Application()
        app.router.add_post('/', self.post)
        app.router.add_get('/', self.get)
        app.router.add_get('/get/proxy/', self.get_proxies_html)
        app.router.add_get('/get/proxy_count_item/', self.get_proxy_count_items_html)

        server = await loop.create_server(app.make_handler(), self.host, self.port)
        return server

    async def post(self, request):
        client_address = request.transport.get_extra_info('peername')

        try:
            data = await request.json()
            response = _api_request_handler.handle(client_address, data)
        except:
            response = {
                'status': "error",
                'error': "Your request doesn't look like request",
            }

        return aiohttp.web.json_response(response)

    async def get_proxies_html(self, request):
        try:
            html="""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="robots" content="noindex">
            <title>Go away!</title>"""

            html += """
            <style>
            #proxy_table {
                width: 100%;
            }
            #proxy_table td {
                padding: 10px;
            }
            </style>
            """
            html += "</head><body>"
            html += """
            <p>All: {}</p>
            <p>Alive: {}</p>
            """.format(
                session.query(Proxy).count(),
                session.query(Proxy).filter(Proxy.number_of_bad_checks == 0).count()
            )

            html += """<table id="proxy_table">"""
            html += "<thead>"
            html += "<tr>"

            html += "<td>address</td>"
            html += "<td>response_time</td>"
            html += "<td>uptime</td>"
            html += "<td>last_check_time</td>"
            html += "<td>checking_period</td>"
            html += "<td>number_of_bad_checks</td>"
            html += "<td>bad_proxy</td>"

            html += "</tr>"
            html += "</thead>"

            html += "<tbody>"

            current_timestamp = int(time.time())
            proxies = session.query(Proxy)\
                .filter(Proxy.number_of_bad_checks == 0)\
                .order_by(Proxy.response_time)

            i = 0
            for proxy in proxies:
                html += "<tr>"
                html += "<td>{}</td>".format(proxy.address)
                html += "<td>{}ms</td>".format(proxy.response_time / 1000 if proxy.response_time is not None else None)
                html += """<td id="proxy_{}_uptime">{}</td>""".format(i,
                                                    datetime.timedelta(seconds=int(current_timestamp - proxy.uptime)))
                html += """<td id="proxy_{}_last_check_time">{}</td>""".format(i, proxy.last_check_time)
                html += "<td>{}</td>".format(proxy.checking_period)
                html += "<td>{}</td>".format(proxy.number_of_bad_checks)
                html += "<td>{}</td>".format(proxy.bad_proxy)
                html += "</tr>"
                html += """
                <script>
                proxy_{}_last_check_time.textContent = new Date({});
                </script>
                """.format(i, proxy.last_check_time * 1000)
                i += 1

            html += "<tbody>"

            html += "</table>"

            html += "</body></html>"
        except Exception as ex:
            _logger.exception(ex)

        return aiohttp.web.Response(headers={'Content-Type': 'text/html'}, body=html)

    async def get_proxy_count_items_html(self, request):
        try:
            html="""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="robots" content="noindex">
            <title>Go away!</title>"""

            html += """
            <script src="https://pikagraphs.d3d.info/static/core/amcharts/amcharts.js"></script>
            <script src="https://pikagraphs.d3d.info/static/core/amcharts/serial.js"></script>
            <script src="https://pikagraphs.d3d.info/static/core/amcharts/export.min.js"></script>
            <script src="https://pikagraphs.d3d.info/static/core/amcharts/light.js"></script>
            <link rel="stylesheet" href="https://pikagraphs.d3d.info/static/core/amcharts/export.css" type="text/css" media="all" />
            <style>
            #proxy_table {
                width: 100%;
            }
            #proxy_table td {
                padding: 10px;
            }
            </style>
            </head><body>
            """

            html += """
            <!-- Chart code -->
<script>
var data = [
"""
            for proxy_count_item in session.query(ProxyCountItem).order_by(ProxyCountItem.timestamp):
                html += "{"
                html += """
                    "date": new Date({}),
                    "good_proxies_count": {},
                    "bad_proxies_count": {},
                    "dead_proxies_count": {}""".format(
                                proxy_count_item.timestamp * 1000, proxy_count_item.good_proxies_count,
                                proxy_count_item.bad_proxies_count, proxy_count_item.dead_proxies_count)
                html += "},\n"

            html += """
];

var chart = AmCharts.makeChart("chartdiv", {
            "type": "serial",
            "theme": "light",
            "legend": {
                "useGraphSettings": true
            },
            "marginRight": 80,
            "autoMarginOffset": 20,
            "marginTop": 7,
            "dataProvider": data,
            "valueAxes": [{
                "id":"v1",
                "axisColor": "#FF6600",
                "axisThickness": 2,
                "axisAlpha": 1,
                "position": "left"
            }, {
                "id":"v2",
                "axisColor": "#FCD202",
                "axisThickness": 2,
                "axisAlpha": 1,
                "position": "right"
            }, {
                "id":"v3",
                "axisColor": "#FF0000",
                "axisThickness": 2,
                "axisAlpha": 1,
                "position": "right"
            }
            ],
            "mouseWheelZoomEnabled": false,
            "graphs": [{
                "id": "v1",
                "balloonText": "[[value]]",
                "bullet": "round",
                "bulletBorderAlpha": 1,
                "bulletColor": "#0f0",
                "hideBulletsCount": 50,
                "title": "good",
                "valueField": "good_proxies_count",
                "useLineColorForBulletBorder": true,
                "balloon":{
                    "drop":true
                }
            },{
                "id": "v2",
                "balloonText": "[[value]]",
                "bullet": "round",
                "bulletBorderAlpha": 1,
                "bulletColor": "#ff0",
                "hideBulletsCount": 50,
                "title": "bad",
                "valueField": "bad_proxies_count",
                "useLineColorForBulletBorder": true,
                "balloon":{
                    "drop":true
                }
            },{
                "id": "v3",
                "balloonText": "[[value]]",
                "bullet": "round",
                "bulletBorderAlpha": 1,
                "bulletColor": "#FF0000",
                "hideBulletsCount": 50,
                "title": "dead",
                "valueField": "dead_proxies_count",
                "useLineColorForBulletBorder": true,
                "balloon":{
                    "drop":true
                }
            }
            ],
            "chartScrollbar": {
                "autoGridCount": true,
                "graph": "v1",
                "scrollbarHeight": 40
            },
            "chartCursor": {
               "limitToGraph":"v1"
            },
            "categoryField": "date",
            "categoryAxis": {
                "minPeriod": "mm",
                "parseDates": true,
                "axisColor": "#DADADA",
                "dashLength": 1,
                "minorGridEnabled": true
            },
            "export": {
                "enabled": true
            }
        });

chart.addListener("dataUpdated", zoomChart);
zoomChart();


function zoomChart(){
    chart.zoomToIndexes(chart.dataProvider.length - 20, chart.dataProvider.length - 1);
}

</script>
<!-- HTML -->
<div id="chartdiv" style="height: 500px; width: 100%;"></div>	
            """

            html += """<table id="proxy_table">"""
            html += "<thead>"
            html += "<tr>"

            html += "<td>timestamp</td>"
            html += "<td>good_proxies_count</td>"
            html += "<td>bad_proxies_count</td>"
            html += "<td>dead_proxies_count</td>"

            html += "</tr>"
            html += "</thead>"

            html += "<tbody>"

            i = 0
            for proxy_count_item in session.query(ProxyCountItem).order_by(ProxyCountItem.timestamp):
                html += "<tr>"
                html += """<td id="proxy_count_item_{}_timestamp">{}</td>""".format(i, proxy_count_item.timestamp)
                html += "<td>{}</td>".format(proxy_count_item.good_proxies_count)
                html += "<td>{}</td>".format(proxy_count_item.bad_proxies_count)
                html += "<td>{}</td>".format(proxy_count_item.dead_proxies_count)
                html += "</tr>"
                html += """
                <script>
                proxy_count_item_{}_timestamp.textContent = new Date({});
                </script>
                """.format(i, proxy_count_item.timestamp * 1000)
                i += 1

            html += "<tbody>"
            html += "</table>"
            html += "</body></html>"
        except Exception as ex:
            _logger.exception(ex)

        return aiohttp.web.Response(headers={'Content-Type': 'text/html'}, body=html)

    async def get(self, request):
        return aiohttp.web.Response(headers={'Content-Type': 'text/html'}, body="""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Go away!</title>
<style>
html, body {
    width: 100%;
    height: 100%;
    background: #eee;
    padding: 0;
    margin: 0;
    line-height: 0;
}
</style>
</head>
<body>

<iframe width="100%" height="100%" src="https://www.youtube.com/embed/7OBx-YwPl8g?rel=0&autoplay=1" frameborder="0" 
allowfullscreen></iframe>
</body>

</html>
""")
