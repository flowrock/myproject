from gevent import monkey; monkey.patch_all()
import gevent
import urllib2
import time
import requests


def fetch(page, url):
    status = None
    result = None
    try :
        response = requests.get(url,timeout=3)
        status = response.status_code
        result = response.json()
    except Exception, e :
        print "reconnect page %d" % page
        fetch(page,url)
        return None
    print "get page %d"%page
    if page==1 and status==200:
        return result['followers_pages']
    else:
        return result


def asynchronous():
    url = 'https://api.500px.com/v1/users/8275495/followers?fullformat=1&rpp=100'
    total_pages = fetch(1, url+"&page=1")
    print "total pages is ", total_pages
    if total_pages is not None and total_pages > 1:
        jobs = []
        for page in range(2,total_pages+1):
            jobs.append(gevent.spawn(fetch, page, url+"&page="+str(page)))
        gevent.joinall(jobs)

start = time.time()
asynchronous()
stop = time.time()
print stop-start