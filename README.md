# proxy_py

proxy_py is a programm which collects proxies and saves them in database. It has server for getting proxies with nice API(see below). 

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

`mv proxy_py/settings.py.example proxy_py/settings.py`

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
It will return following json response:
```
{
	'status': 'ok',
	'count': 1,
	'last_page': True,
	'data': [
		{
			# proxy data
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

json_data = {
	'model': 'proxy',
	'method': 'get',
}

response = json.loads(requests.post('http://example.com:55555', json=json_data).text)
if response['status'] == 'ok':
	for proxy in response['data']:
		print(proxy['address'])
```
Example using aiohttp library:
TODO: do it

## How to deploy on production using supervisor and nginx?

1 Install supervisor and nginx

`apt install supervisor nginx`

2 Copy supervisor config example and change it for your case

```
cp proxy_py/proxy_py.supervisor.conf.example /etc/supervisor/conf.d/proxy_py.conf
vim /etc/supervisor/conf.d/proxy_py.conf
```

3 Copy nginx config example, enable it and change if you need

```
cp proxy_py/proxy_py.nginx.conf.example /etc/nginx/sites-available/proxy_py
ln -s /etc/nginx/sites-available/proxy_py /etc/nginx/sites-enabled/
vim /etc/nginx/sites-available
```

4 Restart supervisor and nginx

```
supervisorctl reread
supervisorctl update
/etc/init.d/nginx configtest
/etc/init.d/nginx restart
```

5 Enjoy using it on your server!
