"""
Default settings for package proxies_handler
"""

# address to take proxies from and send responses to
listen_socket_address = "tcp://127.0.0.1:65535"
# address to send results to
publish_socket_address = "tcp://127.0.0.1:65533"

number_of_workers = 4
# number_of_workers = 1
