from checkers.base_checker import CheckerResult
from proxy_py import settings


async def check_proxy(proxy_url: str, timeout=None) -> tuple:
    results = []

    for checker in settings.PROXY_CHECKERS:
        result = await checker().check(proxy_url, timeout=timeout)
        if result[0] and settings.PROXY_CHECKING_CONDITION == 'or':
            return result

        results.append(result)

    additional_information = CheckerResult()

    if settings.PROXY_CHECKING_CONDITION == 'and':
        for result in results:
            if not result[0]:
                return False, additional_information

            additional_information.update_from_other(result[1])

        return True, additional_information

    return False, additional_information
