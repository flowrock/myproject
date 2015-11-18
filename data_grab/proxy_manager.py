import proxy_factory
import threading
from Queue import Queue
from global_data import THREAD_NUM

MINIMUM_PROXIES = 5

class ProxyManager(object):
    def __init__(self):
        self.proxy_list = []
        self.available_proxies = Queue()

    #remove unavailabel proxy from the dictionary
    def remove_proxy(self, proxy):
        if proxy in self.available_proxies:
            self.available_proxies.pop(proxy)
        if len(self.available_proxies) < MINIMUM_PROXIES:
            self.get_new_proxies()

    def get_new_proxies(self):
        proxy_dict = proxy_factory.get_available_proxies()
        for proxy in proxy_dict:
            print proxy
            self.available_proxies.put(proxy)

    def current_available_proxies(self, thread, order):
        return self.available_proxies

def refresh_proxies():
    pm = ProxyManager()
    t = threading.Thread(target=pm.get_new_proxies())
    t.start()
    t.join()
