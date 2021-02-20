import asyncio
import sys


from models import raw_db


async def worker():
    while True:
        try:
            raw_db.execute_sql("REFRESH MATERIALIZED VIEW working_proxies")
            await asyncio.sleep(60)
        except BaseException as ex:
            sys.stderr.write(str(ex) + "\n")
            await asyncio.sleep(60 * 10)
