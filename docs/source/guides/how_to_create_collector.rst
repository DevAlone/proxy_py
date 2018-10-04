proxy_py How to create a collector
==================================

Collector is a class which is used to parse proxies from web page or another source.
All collectors are inherited from `collectors.abstract_collector.AbstractCollector`,
also there is `collectors.pages_collector.PagesCollector` which is used for paginated sources.
It's always better to learn through the examples.

Simple collector
****************

Let's start with the simplest collector we can imagine,
it will be collecting from the page http://www.89ip.cn/ti.html
as you can see, it sends form as GET request to this url
http://www.89ip.cn/tqdl.html?num=9999&address=&kill_address=&port=&kill_port=&isp=

Firstly we can try to check that these proxies are really good.
Just copy and paste list of proxies to file say /tmp/proxies and run this command inside virtual environment

.. code-block:: bash

    cat /tmp/proxies | python3 check_from_stdin.py

You're gonna get something like this:

`++++++++++++++++++++++-+++++-+++++++++++++++++++++++++++-++++++-++++-+++++++++++++++++++++++++++++++--+++++++-+++++++-++-+-+++-+++++++++-+++++++++++++++++++++--++--+-++++++++++++++++-+++--+++-+-+++++++++++++++++--++++++++++++-+++++-+++-++++++++-+++++-+-+++++++-++-+--++++-+++-++++++++++-++++--+++++++-+++++++-++--+++++-+-+++++++++++++++++++++-++-+++-+++--++++--+++-+++++++-+++++++-+++++++++++++++---+++++-+++++++++-+++++-+-++++++++++++-+--+++--+-+-+-++-+++++-+++--++++++-+++++++++++--+-+++-+-++++--+++++--+++++++++-+-+-++++-+-++++++++++++++-++-++++++--+--++++-+-++--++--+++++-++-+++-++++--++--+---------+--+--++--------+++-++-+--++++++++++++++++-+++++++++-+++++++--+--+--+-+-+++---++------------------+--+----------+-+-+--++-+----------+-------+--+------+----+-+--+--++----+--+-++++++-++-+++`

"\+" means working proxy with at least one protocol, "\-" means not working, the result above is perfect, so many good proxies.

Note: working means proxy respond with timeout set in settings,
if you increase it, you're likely to get more proxies.

Alright, let's code!

We need to place our collector inside `collectors/web/`
directory using reversed domain path,
it will be `collectors/web/cn/89ip/collector.py`

To make class be a collector we need to declare a variable
`__collector__` and set it to `True`

Note: name of file and name of class don't make sense,
you can declare as many files and classes in each file
per domain as you want

.. code-block:: python

    from collectors import AbstractCollector


    class Collector(AbstractCollector):
        __collector__ = True

We can override default processing period in constructor
like this:

.. code-block:: python

    def __init__(self):
        super(Collector, self).__init__()
        # 30 minutes
        self.processing_period = 30 * 60
        '''
        floating period means proxy_py will be changing
        period to not make extra requests and handle
        new proxies in time, you don't need to disable
        it in most cases
        '''
        # self.floating_processing_period = False


The last step is to implement `collect()` method.
Import useful things

.. code-block:: python

    from parsers import RegexParser

    import http_client


and implement method like this:

.. code-block:: python

    async def collect(self):
        url = 'http://www.89ip.cn/tqdl.html?num=9999&address=&kill_address=&port=&kill_port=&isp='
        # send a request to get html code of the page
        html = await http_client.get_text(url)
        # and just parse it using regex parser with a default rule to parse
        # proxies like this:
        # 8.8.8.8:8080
        return RegexParser().parse(html)

That's all!

Now is time for a little test, to be sure your collector is working
you can run proxy_py with `--test-collector` option:

.. code-block:: bash

    python3 main.py --test-collector collectors/web/cn/89ip/collector.py:Collector

which means to take class Collector from the file `collectors/web/cn/89ip/collector.py`

It's gonna draw you a pattern like this:

.. image:: https://i.imgur.com/fmVp3Iz.png

Where red cell means not working proxy

- cyan - respond within a second
- green - slower than 5 seconds
- yellow - up to 10 seconds
- magenta - slower than 10 seconds

Note: don't forget that settings.py limits amount of time
for proxy to respond.
You can override proxy checking timeout by using
`--proxy-checking-timeout` option. For example

.. code-block:: bash

    python3 main.py --test-collector collectors/web/cn/89ip/collector.py:Collector --proxy-checking-timeout 60

With 60 seconds timeout it looks better

.. image:: https://i.imgur.com/DmNuzOI.png

Paginated collector
*******************

Alright, you've done with a simple collector,
you're almost a pro, let's now dive a little deeper

# TODO: complete this guide
