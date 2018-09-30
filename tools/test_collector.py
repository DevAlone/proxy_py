import proxy_validator
from collectors_list import collectors

import re
import sys

from parsers.regex_parser import RegexParser


def eprint(*args, **kwargs):
    return print(*args, file=sys.stderr, **kwargs)


async def run(path: str):
    path, class_name = path.split(':', maxsplit=2)
    path = re.sub(r"\.py$", "", path).replace('/', '.')
    path += '.' + class_name

    try:
        collector = collectors[path]
    except KeyError:
        eprint("Collector doesn't exist")
        return 1

    result = list(await collector.collect())


    for proxy in result:
        try:
            proxy_validator.retrieve(proxy)
        except proxy_validator.ValidationError as ex:
            raise ValueError(
                "Your collector returned bad proxy \"{}\". Message: \"{}\"".format(proxy, ex)
            )

    print("Good job, your collector is awesome!")
