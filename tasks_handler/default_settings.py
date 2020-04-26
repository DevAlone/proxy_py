"""
Default settings for package tasks_manager
"""

# address of socket where tasks_handler puts tasks
proxies_to_check_socket_address = "tcp://127.0.0.1:65535"

# address of socket where proxies_handler puts results
check_results_socket_address = "tcp://127.0.0.1:65534"

results_to_handle_socket_address = "tcp://127.0.0.1:65533"

# number_of_workers = 4
number_of_workers = 1

# TODO: 2 * proxy checking timeout
task_processing_timeout = 60
