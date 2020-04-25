import zmq
import zmq.asyncio

import settings
from handler import handler


async def main() -> int:
    return 1

# async def main() -> int:
#     return await handler(
#         handler_name="results_handler",
#         worker=worker,
#         number_of_workers=settings.results_handler.number_of_workers,
#         socket_type=zmq.???,
#         socket_address=settings.results_handler.socket_address,
#     )
#
#
# async def worker(socket: zmq.asyncio.Socket):
#     while True:
#         # TODO: handle the results
#         pass
