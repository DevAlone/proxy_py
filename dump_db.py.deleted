from proxy_py import settings

import json
import os
import asyncio
import aiopg
import sys


dsn = 'dbname={} user={} password={} host=127.0.0.1'.format(
    settings.DATABASE_CONNECTION_KWARGS['database'],
    settings.DATABASE_CONNECTION_KWARGS['user'],
    settings.DATABASE_CONNECTION_KWARGS['password'],
)


async def dump_it(table_name, save_dir):
    print("start dumping table {}".format(table_name))

    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * from {}".format(table_name))
            # ret = []
            column_names = [desc[0] for desc in cur.description]
            print("found columns: {}".format(column_names))

            file_path = os.path.join(save_dir, table_name + ".json")
            print("writing to file {}".format(file_path))
            with open(file_path, 'w') as file:
                file.write("[\n")
                async for row in cur:
                    json_obj = {
                        column_name: row[i]
                        for i, column_name in enumerate(column_names)
                    }

                    file.write("{},\n".format(json.dumps(json_obj)))

                file.write("]\n")

    print()


async def main():
    if len(sys.argv) < 2:
        raise BaseException("Please, specify directory where to save your dump")

    save_to_dir = sys.argv[1]
    if not os.path.isdir(save_to_dir):
        raise BaseException("{} is not a directory".format(save_to_dir))

    await dump_it('proxies', save_to_dir)
    await dump_it('proxy_count_items', save_to_dir)
    await dump_it('collector_states', save_to_dir)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
