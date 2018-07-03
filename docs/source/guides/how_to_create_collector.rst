proxy_py How to create collector
================================

Collector is a class which is used to parse proxies from web page or another source. All collectors are inherited from `collectors.abstract_collector.AbstractCollector`, also there is `collectors.pages_collector.PagesCollector` which is used for paginated sources. It's better to understand through examples.

Simple collector
****************

Let's start with the simplest collector we can imagine, it will be from the page http://www.89ip.cn/ti.html as you can see, it sends form as GET request to this url http://www.89ip.cn/tqdl.html?num=9999&address=&kill_address=&port=&kill_port=&isp= 

Firstly we can try to check that these proxies are really good. Just copy and paste list of proxies to file say /tmp/proxies and run this command inside virtual environment

.. code-block:: bash

    cat /tmp/proxies | python3 check_from_stdin.py

You're gonna get something like this:

`++++++++++++++++++++++-+++++-+++++++++++++++++++++++++++-++++++-++++-+++++++++++++++++++++++++++++++--+++++++-+++++++-++-+-+++-+++++++++-+++++++++++++++++++++--++--+-++++++++++++++++-+++--+++-+-+++++++++++++++++--++++++++++++-+++++-+++-++++++++-+++++-+-+++++++-++-+--++++-+++-++++++++++-++++--+++++++-+++++++-++--+++++-+-+++++++++++++++++++++-++-+++-+++--++++--+++-+++++++-+++++++-+++++++++++++++---+++++-+++++++++-+++++-+-++++++++++++-+--+++--+-+-+-++-+++++-+++--++++++-+++++++++++--+-+++-+-++++--+++++--+++++++++-+-+-++++-+-++++++++++++++-++-++++++--+--++++-+-++--++--+++++-++-+++-++++--++--+---------+--+--++--------+++-++-+--++++++++++++++++-+++++++++-+++++++--+--+--+-+-+++---++------------------+--+----------+-+-+--++-+----------+-------+--+------+----+-+--+--++----+--+-++++++-++-+++`

+ means working proxy with at leat one protocol, - means not working, the result above is perfect, so many good proxies.

Note: working means proxy respond with timeout set in settings, if you increase it you'll get more proxies.

Paginated collector
*******************

So, let's create a simple paginated collector. 


