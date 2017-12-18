from models import session, Proxy
import sys
import base64
import json
import sqlalchemy


if  __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 {} RESULT_FILE".format(sys.argv[0] if len(sys.argv) == 1 else "program"))
        exit(1)

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
                session.add(proxy)
                session.commit()
            except sqlalchemy.exc.IntegrityError:
                session.rollback()
                print("proxy {} exists".format(proxy))

            i += 1
