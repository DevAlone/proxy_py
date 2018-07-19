proxy_py How to create collector
================================

Collector is a class which is used to parse proxies from web page or another source.
All collectors are inherited from `collectors.abstract_collector.AbstractCollector`,
also there is `collectors.pages_collector.PagesCollector` which is used for paginated sources.
It's better to understand through examples.

Simple collector
****************

Let's start with the simplest collector we can imagine,
it will be from the page http://www.89ip.cn/ti.html as you can see,
it sends form as GET request to this url
http://www.89ip.cn/tqdl.html?num=9999&address=&kill_address=&port=&kill_port=&isp=

Firstly we can try to check that these proxies are really good.
Just copy and paste list of proxies to file say /tmp/proxies and run this command inside virtual environment

.. code-block:: bash

    cat /tmp/proxies | python3 check_from_stdin.py

You're gonna get something like this:

`++++++++++++++++++++++-+++++-+++++++++++++++++++++++++++-++++++-++++-+++++++++++++++++++++++++++++++--+++++++-+++++++-++-+-+++-+++++++++-+++++++++++++++++++++--++--+-++++++++++++++++-+++--+++-+-+++++++++++++++++--++++++++++++-+++++-+++-++++++++-+++++-+-+++++++-++-+--++++-+++-++++++++++-++++--+++++++-+++++++-++--+++++-+-+++++++++++++++++++++-++-+++-+++--++++--+++-+++++++-+++++++-+++++++++++++++---+++++-+++++++++-+++++-+-++++++++++++-+--+++--+-+-+-++-+++++-+++--++++++-+++++++++++--+-+++-+-++++--+++++--+++++++++-+-+-++++-+-++++++++++++++-++-++++++--+--++++-+-++--++--+++++-++-+++-++++--++--+---------+--+--++--------+++-++-+--++++++++++++++++-+++++++++-+++++++--+--+--+-+-+++---++------------------+--+----------+-+-+--++-+----------+-------+--+------+----+-+--+--++----+--+-++++++-++-+++`

+ means working proxy with at least one protocol,
- means not working, the result above is perfect, so many good proxies.

Note: working means proxy respond with timeout set in settings, if you increase it you'll get more proxies.

Alright, let's code it!

We need to place our collector inside `collectors/web/` directory using reversed domain path,
it will be `collectors/web/cn/89ip/collector.py`

To make class be collector we need to declare variable `__collector__`

Note: name of file and name of class don't make sense,
you can declare as many files and classes in each file per domain as you want

.. code-block:: python

    from collectors.abstract_collector import AbstractCollector


    class Collector(AbstractCollector):
        __collector__ = True

We can override default processing period in constructor like this:

.. code-block:: python

    def __init__(self):
        super(Collector, self).__init__()
        self.processing_period = 30 * 60  # 30 minutes
        '''
        floating period means proxy_py will be changing
        period to not make extra requests and handle
        new proxies in time, you don't need to change
        it in most cases
        '''
        # self.floating_processing_period = False


Paginated collector
*******************

So, let's create a simple paginated collector. 


