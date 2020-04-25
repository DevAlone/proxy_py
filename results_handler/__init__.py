"""
proxies_handler package takes tasks from existing and new proxies queues(existing have higher priority), checks them
and puts results to results queue.
"""

from .results_handler import main
