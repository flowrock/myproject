import proxy_factory
import threading

available_proxies = {}
MINIMUM_PROXIES = 5

class ProxyManager(object):
    def __init__(self):
        pass

    #remove unavailabel proxy from the dictionary
    def remove_proxy(self, proxy):
        global available_proxies
        if proxy in available_proxies:
            available_proxies.pop(proxy)
        if len(available_proxies) < MINIMUM_PROXIES:
            get_new_proxies()

    def get_new_proxies(self):
        global available_proxies
        available_proxies = proxy_factory.get_available_proxies()

    def current_available_proxies(self):
        global available_proxies
        return available_proxies

def refresh_proxies():
    pm = ProxyManager()
    t = threading.Thread(target=pm.get_new_proxies())
    t.start()
    t.join()
