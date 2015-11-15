import urllib2
import time
from selenium import webdriver
import multiprocessing
from multiprocessing import Process, Queue

class Proxy:
    def __init__(self, addr, time):
        self.address = addr
        self.time = time
    def __lt__(self, other):
         return self.time < other.time

class ProxyFactory:
    def __init__(self):
        self.pool = []
        self.proxyPairs = []
    
    def Run(self):
        proxyList = self.FetchProxies()
        self.ValidateProxies(proxyList)
        
        self.pool.sort()
        
        for i in self.pool:
            self.proxyPairs += [(i.address, i.time)]


    def FetchProxies(self):
        u = "http://www.freeproxylists.net/zh/?c=us&f=1&s=u"
        driver = webdriver.phantomjs.webdriver.WebDriver(executable_path="/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs")
        driver.get(u)
        rows = driver.find_elements_by_css_selector("table > tbody > tr")
        proxies = []
        for i in rows:
            if i.text.find("HTTP") != -1:
                cells = i.text.split()
                proxies += [u"http://{0}:{1}".format(cells[0], cells[1])]
        proxies = proxies[1:]
        return proxies
    
    def CheckProxy(self, address, tests, result):
        for t in tests:
            proxy=urllib2.ProxyHandler({'http': address})
            opener=urllib2.build_opener(proxy, urllib2.HTTPHandler)
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36')]
            try:
                start = time.clock()
                data = opener.open(t, timeout = 5).read().decode()
                end = time.clock()
                result.put((address, end - start))
            except Exception as e:
                continue

    def ValidateProxies(self, proxyList):
        maxProc = 5
        tests = ["http://www.google.com"]
        result = Queue()
        
        for i in proxyList:
            p = Process(target=self.CheckProxy, args=(i, tests, result))
            p.start()  
            
            if len(multiprocessing.active_children()) > maxProc:
                p.join()
            
        while len(multiprocessing.active_children()) > 0:
            time.sleep(3)
        
        self.pool = []
        
        while not result.empty():
            a = result.get()
            self.pool += [Proxy(a[0], a[1])]
    
def get_available_proxies():
    pf = ProxyFactory()
    pf.Run()
    return pf.proxyPairs

