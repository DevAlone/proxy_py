try:
    from .user_settings import *
except ModuleNotFoundError:
    from .default_settings import *
