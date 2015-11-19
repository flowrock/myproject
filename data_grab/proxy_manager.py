import proxy_factory
import threading
import time
from Queue import Queue
from global_data import THREAD_NUM

class ProxyManager(object):
    def __init__(self):
        self.capacity = THREAD_NUM*3
        self.proxy_list = []
        self.available_proxies = Queue()
        self.order_map = {}
        for i in xrange(THREAD_NUM):
            self.order_map[i] = 0

    #remove unavailabel proxy from the dictionary
    def remove_proxy(self, proxy):
        if proxy in self.proxy_list:
            self.proxy_list.remove(proxy)
        self.refill_proxy_list()

    def retrieve_new_proxies(self):
        proxy_dict = proxy_factory.get_available_proxies()
        for proxy in proxy_dict:
            if len(self.proxy_list) < self.capacity:
                self.proxy_list.append(proxy)
            else:
                self.available_proxies.put(proxy)

    def get_proxy(self, thread):
        order = self.order_map[thread]
        self.order_map[thread] = (order+1)%3
        pos = order*THREAD_NUM+thread
        while pos >= len(self.proxy_list):
            pos -= THREAD_NUM
        if pos < 0:
            self.retrieve_new_proxies()
            return None
        else:
            return self.proxy_list[pos]

    def refresh_proxies(self):
        last_update = time.time()
        while True:
            now = time.time()
            if now-last_update > 30:
                self.retrieve_new_proxies()
                self.proxy_list = []
                self.refill_proxy_list()
                last_update = now
            else:
                time.sleep(10)

    def refill_proxy_list(self):
        while len(self.proxy_list)<self.capacity and not self.available_proxies.empty():
            self.proxy_list.append(self.available_proxies.get())


