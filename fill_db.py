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


async def fill_it(dir_path, table_name):
    print("start filling table {}".format(table_name))

    pool = await aiopg.create_pool(dsn)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # await cur.execute()

            file_path = os.path.join(dir_path, table_name + ".json")

            print("reading file {}".format(file_path))
            with open(file_path) as file:
                print("filling database", end="")
                for i, line in enumerate(file):
                    print(".", end="")
                    sys.stdout.flush()

                    line = line.strip()
                    if line and line not in '[]':
                        line = line[:-1]
                        json_obj = json.loads(line)
                        # print(json_obj)
                        keys = []
                        values = []
                        for key, val in json_obj.items():
                            keys.append(key)
                            values.append(val)

                        sql_request = """
                            INSERT INTO {} ({})
                            VALUES ({})
                            ON CONFLICT DO NOTHING; 
                        """.format(table_name, ', '.join(keys), ', '.join(['%s' for _ in range(len(values))]))

                        # print(sql_request.strip())

                        await cur.execute(sql_request, values)

                print()

    print()


async def main():
    if len(sys.argv) < 2:
        raise BaseException("Please, specify directory from which to load your dumps")

    load_from_dir = sys.argv[1]
    if not os.path.isdir(load_from_dir):
        raise BaseException("{} is not a directory".format(load_from_dir))

    for filename in [filename for filename in os.listdir(load_from_dir)
                     if os.path.isfile(os.path.join(load_from_dir, filename))]:
        table_name, _ = filename.split(".")
        await fill_it(load_from_dir, table_name)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
