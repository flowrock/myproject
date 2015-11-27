from gevent import monkey; monkey.patch_all()
import gevent
import urllib2
import time

def f(url):
    resp = urllib2.urlopen(url)
    data = resp.read()

def sync_proc():
    for i in xrange(100):
        f('https://www.python.org/')

def async_proc():
    jobs = []
    for i in xrange(100):
        jobs.append(gevent.spawn(f, 'https://www.python.org/'))
    gevent.joinall(jobs)

start = time.time()
sync_proc()
print 'sync time'
print time.time()-start

start = time.time()
async_proc()
print "async time"
print time.time()-start