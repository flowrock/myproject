from gevent import monkey; monkey.patch_all()
import gevent
import urllib2
import time
from selenium import webdriver

class ProxyFactory:
    def __init__(self):
        self.available_proxies = {}
    
    def Run(self):
        proxyList = self.FetchProxies()
        self.ValidateProxies(proxyList)

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
    
    def CheckProxy(self, address, url):
        proxy=urllib2.ProxyHandler({'http': address})
        opener=urllib2.build_opener(proxy, urllib2.HTTPHandler)
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36')]
        try:
            start = time.clock()
            data = opener.open(url, timeout = 3)
            end = time.clock()
            self.available_proxies[address] = end-start
            # print "OK"
        except Exception as e:
            # print "unavailable"
    
    def ValidateProxies(self, proxyList):
        url = "https://api.500px.com/v1/users/9149967/followers?fullformat=1"
        start = time.clock() 
        jobs = []
        for address in proxyList:
            jobs.append(gevent.spawn(self.CheckProxy, address, url)) 
        gevent.joinall(jobs)     
        end = time.clock()
        
    
def get_available_proxies():
    pf = ProxyFactory()
    pf.Run()
    return pf.available_proxies
