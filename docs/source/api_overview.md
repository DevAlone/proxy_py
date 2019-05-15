# proxy_py API v1

proxy_py expects HTTP POST requests with JSON as a body, so you need
to add header `Content-Type: application/json` and send correct
JSON document.

Example of correct request:
```json
{
  "method": "get",
  "model": "proxy"
}
```

Response is also HTTP with JSON and status code depending on whether
error happened or not.

* 200 if there wasn't error
* 400 if you sent a bad request
* 500 if there was an error during execution your request or in some
other cases

status_code is also duplicated in JSON body.

## Possible keys

* `model` - specifies what you will work with.
Now it's only supported to work with `proxy` model.
* `method` - what you're gonna do with it
  * `get` - get model items as json objects.
  Detailed description is below
  * `count` - count how many items there are.
  Detailed description is below


### get method

`get` method supports the following keys:
* `order_by` (string) - specifies ordering fields as comma separated ("response_time" if not provided)
value.

Explanation:

`"uptime"` just sorts proxies by uptime field ascending.

Note: `uptime` is the timestamp from which proxy is working,
NOT proxy's working time

To sort descending use `-`(minus) before the field name.

`"-response_time"` returns proxies with maximum response_time first
(in microseconds)

It's also possible to sort using multiple fields

`"number_of_bad_checks, response_time"` returns proxies with minimum
`number_of_bad_checks` first, if there are proxies with the same
`number_of_bad_checks`, sorts them by `response_time`

* `limit` (integer) -  specifies how many proxies to return (1024 if not provided)
* `offset` (integer) - specifies how many proxies to skip (0 if not provided)

Example of `get` request:

```json

{
    "model": "proxy",
    "method": "get",
    "order_by": "number_of_bad_checks, response_time",
    "limit": 100,
    "offset": 200
}
```

Response

```json
{
    "count": 6569,
    "data": [
        {
            "address": "socks5://localhost:9999",
            "auth_data": "",
            "bad_proxy": false,
            "domain": "localhost",
            "last_check_time": 1517089048,
            "number_of_bad_checks": 0,
            "port": 9999,
            "protocol": "socks5",
            "response_time": 1819186,
            "uptime": 1517072132
        },

        ...

    ],
    "has_more": true,
    "status": "ok",
    "status_code": 200
}
```

Response fiels:

* `count` (integer) - total number of proxies for that request(how many you can fetch increasing offset)
* `data` (array) - list of proxies
* `has_more` (boolean) - value indicating whether you can increase
offset to get more proxies or not
* `status` (string) - "error" if error happened, "ok" otherwise

Example of error:

Request:

```json
{
    "model": "user",
    "method": "get",
    "order_by": "number_of_bad_checks, response_time",
    "limit": 100,
    "offset": 200
}
```

Response:

```json
{
    "error_message": "Model \"user\" doesn't exist or isn't allowed",
    "status": "error",
    "status_code": 400
}
```

### count method

Same as get, but doesn't return data

# proxy_py API v2

Second version of API has only 2 methods so far 

```bash
curl https://localhost:55555/api/v2/get_proxy_for_id --data '{"id": "ID"}'
```            
```bash
curl https://localhost:55555/api/v2/get_proxies_for_id --data '{"id": "ID", "number": 2}'
```

get_proxy_for_id should return the best proxy for a given ID avoiding overlapping with other IDs, but so far it just returns a random one ignoring ID at all.
get_proxies_for_id is the same, but also has a parameter `number` to specify the number of proxies to return.
