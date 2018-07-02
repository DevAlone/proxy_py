import copy

from checkers.base_checker import CheckerResult
from proxy_py import settings
import random


async def check_proxy(proxy_url: str, timeout=None) -> tuple:
    if not settings.PROXY_CHECKERS:
        raise Exception('add at least one checker')

    checkers = copy.copy(settings.PROXY_CHECKERS)
    random.shuffle(checkers)
    results = []

    for checker, _ in zip(checkers, range(settings.MINIMUM_NUMBER_OF_CHECKERS_PER_PROXY)):
        result = await checker().check(proxy_url, timeout=timeout)
        if not result[0]:
            return False, None

        results.append(result)

    additional_information = CheckerResult()

    for result in results:
        additional_information.update_from_other(result[1])

    return True, additional_information
