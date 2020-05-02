import copy
import random

from .checkers.base_checker import CheckerResult
import settings


async def check_proxy(proxy_url: str, timeout=None) -> tuple:
    if not settings.proxies_handler.proxy_checkers:
        raise Exception('add at least one checker')

    checkers = copy.copy(settings.proxies_handler.proxy_checkers)
    random.shuffle(checkers)
    results = []

    for checker, _ in zip(checkers, range(settings.proxies_handler.minimum_number_of_checkers_per_proxy)):
        checker()
        result = await checker().check(proxy_url, timeout=timeout)
        if not result[0]:
            return False, None

        results.append(result)

    additional_information = CheckerResult()

    for result in results:
        additional_information.update_from_other(result[1])

    return True, additional_information
