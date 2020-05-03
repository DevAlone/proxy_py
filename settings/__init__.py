"""
Default settings for each module(including the root) are in file default_settings.py,
one can override them by creating a file user_settings with the following content:

```python3
from .default_settings import *

# override settings here
```
"""

from collectors_handler import settings as collectors_handler
from proxies_handler import settings as proxies_handler
from tasks_handler import settings as tasks_handler
from results_handler import settings as results_handler
from server import settings as server

try:
    from .user_settings import *
except ModuleNotFoundError:
    from .default_settings import *
