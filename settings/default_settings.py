from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

log_level = INFO
log_format = "%(asctime)s - [%(levelname)s] - %(module)s - %(pathname)s - " \
             "%(funcName)s():%(lineno)d - %(message)s"

postgres_credentials = {
    "user": "proxy_py",
    "password": "proxy_py",
    "database": "proxy_py",
    "host": "db",
    # 'max_connections': 20,
}

# number of failed checks when proxy is considered dead
dead_proxy_threshold = 10

# TODO: it is not supported by tasks handler yet
do_not_check_on_n_bad_checks = 99999999

"""
Database settings (do not try to change after creation of the database)
"""
geolite2_city_file_location = "/tmp/proxy_py_9910549a_7d41_4102_9e9d_15d39418a5cb/GeoLite2-City.mmdb"

min_proxy_checking_period = 5 * 60
