"""
Default settings for package tasks_manager
"""

# address of socket where tasks_handler puts tasks
proxies_to_check_socket_address = "tcp://0.0.0.0:65535"

# address of socket where proxies-handler puts results
check_results_socket_address = "tcp://0.0.0.0:65534"

results_to_handle_socket_address = "tcp://0.0.0.0:65533"

# TODO: 2 * proxy checking timeout
task_processing_timeout: int = 60

# limits number of messages in queue. But it's not a number of messages
# because there's also kernel buffer size which adds size to queue
# 0 is default value
high_water_mark: int = 0

# size of kernel buffer for send and receive sockets in bytes (0 use OS's default value)
# Kernel can not care about this value
kernel_buffer_size: int = 0

# maximum number of simultaneously checking proxies
proxies_checking_queue_size: int = 1

fetch_n_proxies_at_time: int = 1024
