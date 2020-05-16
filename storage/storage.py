import asyncio
import logging
import typing

import peewee

import settings
from .models import \
    Proxy, ProxyCountItem, CollectorState, \
    NumberOfProxiesToProcess, NumberOfCollectorsToProcess, \
    raw_db, db


class PostgresStorage:
    async def init(self):
        while True:
            try:
                await self.init_db()
                break
            except peewee.OperationalError as ex:
                logging.exception(ex)
                await asyncio.sleep(1)
                continue

    async def init_db(self):
        _silent = True

        raw_db.init(**settings.postgres_credentials)

        Proxy.create_table(_silent)
        ProxyCountItem.create_table(_silent)
        CollectorState.create_table(_silent)
        NumberOfProxiesToProcess.create_table(_silent)
        NumberOfCollectorsToProcess.create_table(_silent)

        raw_db.execute_sql(
            """
                CREATE MATERIALIZED VIEW IF NOT EXISTS working_proxies 
                AS SELECT * FROM proxies WHERE number_of_bad_checks = 0;
            """
        )

    async def close(self):
        raw_db.close()

    async def get_good_proxies_to_check(self, next_update_timestamp, limit) -> typing.List[Proxy]:
        return await self.get_proxies_to_check((0, 0), next_update_timestamp, limit)

    async def get_bad_proxies_to_check(self, next_update_timestamp, limit) -> typing.List[Proxy]:
        return await self.get_proxies_to_check((1, settings.dead_proxy_threshold), next_update_timestamp, limit)

    async def get_dead_proxies_to_check(self, next_update_timestamp, limit) -> typing.List[Proxy]:
        return await self.get_proxies_to_check((settings.dead_proxy_threshold, -1), next_update_timestamp, limit)

    async def get_proxies_to_check(
            self,
            number_of_bad_checks_range: typing.Tuple[int, int],
            next_update_timestamp: int,
            limit: int,
    ) -> typing.List[Proxy]:
        number_of_bad_checks_filters = []

        if number_of_bad_checks_range[0] == number_of_bad_checks_range[1]:
            number_of_bad_checks_filters.append(Proxy.number_of_bad_checks == number_of_bad_checks_range[0])
        else:
            if number_of_bad_checks_range[0] != -1:
                number_of_bad_checks_filters.append(Proxy.number_of_bad_checks >= number_of_bad_checks_range[0])
            if number_of_bad_checks_range[1] != -1:
                number_of_bad_checks_filters.append(Proxy.number_of_bad_checks < number_of_bad_checks_range[1])

        return await db.execute(
            Proxy.select().where(
                *number_of_bad_checks_filters,
                Proxy.next_check_time <= next_update_timestamp,
            ).order_by(Proxy.next_check_time).limit(limit),
        )

    # TODO: remove since the state should be in redis or other in-memory storage
    async def get_collectors_to_check(self, next_update_timestamp, limit) -> typing.List[CollectorState]:
        return await db.execute(
            CollectorState.select().where(
                CollectorState.last_processing_time < next_update_timestamp - CollectorState.processing_period
            ).order_by(peewee.fn.Random()).limit(limit)
        )
