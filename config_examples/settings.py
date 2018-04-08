from ._settings import *

DATABASE_CONNECTION_KWARGS = {
    'database': 'YOUR_POSTGRES_DATABASE',
    'user': 'YOUR_POSTGRES_USER',
    'password': 'YOUR_POSTGRES_PASSWORD',
    # number of simultaneous connections
    # 'max_connections': 20,
}

DEBUG = False
