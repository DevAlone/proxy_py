"""
Default settings for package proxies_handler
"""

# address to get results from
proxies_to_check_socket_address = "tcp://tasks-handler:65535"

# address to push results to
check_results_socket_address = "tcp://tasks-handler:65534"

# number_of_workers = 4
number_of_workers = 1

# limits number of messages in queue. But it's not a number of messages
# because there's also kernel buffer size which adds size to queue
# 0 is default value
high_water_mark = 0

# size of kernel buffer for send and receive sockets in bytes (0 use OS's default value)
# Kernel can not care about this value
kernel_buffer_size = 0
