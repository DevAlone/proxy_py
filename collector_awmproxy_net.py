from .collector import AbstractCollector
import lxml.html
import lxml.etree

import requests


# TODO: add logging
class Collector(AbstractCollector):
    def collect(self):
        try:
            with open('awmproxies') as f:
                return f.read().splitlines()
        except:
            return []
