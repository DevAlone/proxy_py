"""
tasks_manager package produces tasks to check existing proxies and sends them to
proxies_handler through broker.

Do not try to make multiple instances of tasks-handler per cluster, it's not designed to work.
"""

from .main import main
