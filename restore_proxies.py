from proxy_py import settings
from models import session, Proxy
import sys
import base64
import json
import sqlalchemy
import time


if  __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 {} RESULT_FILE".format(sys.argv[0] if len(sys.argv) == 1 else "program"))
        exit(1)

    last_check_time = int(time.time())
    i = 0
    with open(sys.argv[1], 'r') as file:
        for line in file:
            try:
                print("line {}".format(i))
                json_proxy = json.loads(base64.b64decode(line.encode()).decode())
                # print(json_proxy)
                proxy = Proxy()
                proxy._protocol = Proxy.PROTOCOLS.index(json_proxy['protocol'])
                proxy.auth_data = ""
                proxy.domain = json_proxy['domain']
                proxy.port = json_proxy['port']
                proxy.last_check_time = last_check_time
                proxy.last_check_time += 1
                proxy.number_of_bad_checks = settings.REMOVE_ON_N_BAD_CHECKS - 5
                session.add(proxy)
                session.commit()
            except sqlalchemy.exc.IntegrityError:
                session.rollback()
                print("proxy {} exists".format(proxy))

            i += 1
