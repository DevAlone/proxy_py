"""
Default settings for package collectors_handler
"""

# address to push proxies to
collectors_results_socket_address = "tcp://tasks-handler:65532"

number_of_workers = 4

# limits number of messages in queue. But it's not a number of messages
# because there's also kernel buffer size which adds size to queue
# 0 is default value
high_water_mark = 0

# size of kernel buffer for send and receive sockets in bytes (0 use OS's default value)
# Kernel can not care about this value
kernel_buffer_size = 0

# limiter for maximum number of proxies gotten from collector
# to fix potential issue with collectors' spamming
maximum_number_of_proxies_per_request = 65535

# it allows you to override or add your own collectors
# for example if you're making proxy checker for particular site
# you can override COLLECTORS_DIR and PROXY_CHECKERS
collectors_dirs = [
    'collectors',
    # 'local/collectors',  # use to add your own collectors
]
