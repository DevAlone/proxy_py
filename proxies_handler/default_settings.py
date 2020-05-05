"""
Default settings for package proxies_handler
"""

from .checkers import GoogleComChecker

# address to get results from
proxies_to_check_socket_address = "tcp://tasks-handler:65535"

# address to push results to
check_results_socket_address = "tcp://tasks-handler:65534"

# TODO: find the best value here
number_of_workers = 4
number_of_simultaneous_requests = number_of_workers
number_of_simultaneous_requests_per_host = number_of_simultaneous_requests

proxy_checking_timeout = 30


# limits number of messages in queue. But it's not a number of messages
# because there's also kernel buffer size which adds size to queue
# 0 is default value
high_water_mark = 0

# size of kernel buffer for send and receive sockets in bytes (0 use OS's default value)
# Kernel can not care about this value
kernel_buffer_size = 0

# list of proxy checkers, you can override it
proxy_checkers = [
    GoogleComChecker,
]

# how many checkers should say that proxy is working
# to consider it so.
# Should be in range from 1 to len(PROXY_CHECKERS)
# Note: the order of the checkers won't be the same,
# they're shuffled for each proxy
minimum_number_of_checkers_per_proxy = 1
