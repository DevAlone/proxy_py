# proxy_py

proxy_py is a program which collects proxies, saves them in database and makes periodically checks. It has server for getting proxies with nice API(see below). 

## What is it depend on?

```
lxml
pysocks
django
aiohttp
aiosocks
```

## How to build?

1 Clone this repository

`git clone https://github.com/DevAlone/proxy_py.git`

2 Install requirements

```
cd proxy_py
pip3 install -r requirements.txt
```

3 Create settings file

`cp config_examples/settings.py proxy_py/settings.py`

4 (Optional) Change database in settings.py file

5 Create database tables

```
python3 manage.py makemigrations core
python3 manage.py migrate
```

6 Run your application

`python3 main.py`

7 Enjoy!

## How to get proxies?

proxy_py has server based on aiohttp which is listening 127.0.0.1:55555(you can change it in settings file) and provides proxies. To get proxies you should send following json request:

```
{
	'model': 'proxy',
	'method': 'get',
}
```

It will return json response like this:

```
{
	'status': 'ok',
	'count': 1,
	'last_page': True,
	'data': [
		{
			# proxy data
			"address": "http://127.0.0.1:8080",
			"auth_data": null,
			"bad_proxy": false,
			"domain": "127.0.0.1",
			"last_check_time": 1509466165,
			"number_of_bad_checks": 0,
			"port": 8080,
			"protocol": "http",
			"uptime": 1509460949,
			"white_ip_v4": null,
			"white_ip_v6": null,
		}
	]
}
```

Or error if something went wrong:

```
{
	'status': 'error',
	'error': 'You should specify model',
}
```

Example using curl:

`curl -X POST http://example.com:55555 -H "Content-Type: application/json" --data '{"model": "proxy", "method": "get"}'`

Example using httpie:

`http POST http://example.com:55555 model=proxy method=get`

Example using python requests library:

```
import requests
import json


def get_proxies():
    result = []
    json_data = {
        'model': 'proxy',
        'method': 'get',
    }
    
    response = json.loads(requests.post('http://example.com:55555', json=json_data).text)
    if response['status'] == 'ok':
        for proxy in response['data']:
            result.append(proxy['address'])
    
    return result
```
Example using aiohttp library:

```
import aiohttp


async def get_proxies():
    result = []
    json_data = {
        'model': 'proxy',
        'method': 'get',
    }
    
    with aiohttp.ClientSession() as session:
        with session.post('http://example.com:55555', json=json_data) as response:
            response = json.loads(await response.text())
            for proxy in response['data']:
                result.append(proxy['address'])
                
    return result
```

## How to deploy on production using supervisor, nginx and postgresql in 8 steps?

1 Install supervisor, nginx and postgresql

`root@server:~$ apt install supervisor nginx postgresql`

2 Create virtual environment and install requirements on it

3 Install psycopg2

`(proxy_py) proxy_py@server:~/proxy_py$ pip3 install psycopg2`

4 create unprivileged user in postgresql database and add database authentication data to settings.py

```
proxy_py@server:~/proxy_py$ vim proxy_py/settings.py
```

```
from ._settings import *

DATABASES = {                                                                    
        'default': {                                                                 
                'ENGINE': 'django.db.backends.postgresql_psycopg2',                     
                'NAME': 'DB_NAME',                                                     
                'USER': 'USERNAME',                                                     
                'PASSWORD': 'PASSWORD',                                                 
                'HOST': '127.0.0.1',                                                    
                'PORT': '5432',                                                         
        },                                                                           
}
```

5 Copy supervisor config example and change it for your case

```
root@server:~$ cp config_examples/proxy_py.supervisor.conf /etc/supervisor/conf.d/proxy_py.conf
root@server:~$ vim /etc/supervisor/conf.d/proxy_py.conf
```

6 Copy nginx config example, enable it and change if you need

```
root@server:~$ cp config_examples/proxy_py.nginx.conf /etc/nginx/sites-available/proxy_py
root@server:~$ ln -s /etc/nginx/sites-available/proxy_py /etc/nginx/sites-enabled/
root@server:~$ vim /etc/nginx/sites-available/proxy_py
```

7 Restart supervisor and nginx

```
root@server:~$ supervisorctl reread
root@server:~$ supervisorctl update
root@server:~$ /etc/init.d/nginx configtest
root@server:~$ /etc/init.d/nginx restart
```

8 Enjoy using it on your server!
