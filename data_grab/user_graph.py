from gevent import monkey; monkey.patch_all()
import gevent
import multiprocessing
import urllib2
import simplejson
import time
import threading
from Queue import Queue
import user_manager
from proxy_manager import ProxyManager
from db_helper import mydb

bfs_queue = None
proxy_manager = None

count = 1

#the user mining process is an infinite loop
def retrieve_user_from_queue():
    threading_list = []
    for i in range(10):
        t = threading.Thread(target=start_loop, args=(i,))
        threading_list.append(t)
        t.start()
        time.sleep(1)
    for t in threading_list:
        t.join()

def start_loop(thread):
    start = time.time()
    while True:
        if not bfs_queue.empty():
            user = bfs_queue.get()
            global count
            print count
            count+=1
            _request_followers_of_user(user,thread)
        else:
            time.sleep(1)
        # if time.time()-start > 60:
        #     break

def _request_followers_of_user(user,thread):
    url = 'https://api.500px.com/v1/users/'+str(user)+'/followers?fullformat=1&rpp=100'
    global proxy_manager
    proxy_addr = proxy_manager.get_proxy(thread)
    total_pages = _fetch(user, url, 1, 0, proxy_addr)
    if total_pages is not None and total_pages > 1:
        jobs = []
        for page in xrange(2,total_pages+1):
            jobs.append(gevent.spawn(_fetch, user, url+"&page="+str(page), page, 0, proxy_addr))
        gevent.joinall(jobs)
    else:
        bfs_queue.put(user)
        
def _fetch(user, url, page, attempts, proxy_addr):
    pages = None
    followers = None
    result = None
    if attempts >= 3:
        return None
    proxy=urllib2.ProxyHandler({'http': proxy_addr})
    opener=urllib2.build_opener(proxy, urllib2.HTTPHandler)
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36')]
    try:
        response = opener.open(url, timeout = 3).read()
        result = simplejson.loads(response)
        # print "successful getting page %d"%page
        followers = result['followers']
        follower_list = []   
        for follower in followers:
            follower_list.append(follower)
        # _save_follower_relation_to_db(user, follower_list) 
    except Exception, e:
        # print e
        # print "refetch page %d"%page
        return _fetch(user, url, page, attempts+1, proxy_addr)
    return result['followers_pages']

#may want to spawn to separate threads
def _save_follower_relation_to_db(user, follower_list):
    follower_id_list = []

    rejected_fields = ['domain','firstname','lastname','cover_url','thumbnail_background_url','avatars']

    #save users into users collection
    user_collection = mydb.users
    for follower in follower_list:
        follower_id_list.append(follower['id'])
        if not user_manager.user_seen(follower['id']):
            user_manager.add_user(follower['id'])
            bfs_queue.put(follower['id'])
            follower['following'] = [user]
            for field in rejected_fields:
                follower.pop(field, None)
            user_collection.insert(follower)
        else:
            record = user_collection.find_one({'id':follower['id']})
            record['following'].append(user)
            user_collection.save(record)

    #add the following relation of the given user into user relation collection
    user_relation_collection = mydb.user_relation
    record = user_relation_collection.find_one({'user':user})
    if record is None:     
        relation = {}
        relation['user'] = user
        relation['followers'] = follower_id_list
        user_relation_collection.insert(relation)
    else:
        record['followers'].extend(follower_id_list)
        user_relation_collection.save(record)


def user_search_start_running():
    global bfs_queue
    bfs_queue = Queue()
    bfs_queue.put(9149967)

    #start proxy manager
    global proxy_manager
    proxy_manager = ProxyManager()
    proxy_manager.retrieve_new_proxies()
    #start daemon refreshing available proxies
    t = threading.Thread(target=proxy_manager.refresh_proxies)
    t.start()
    retrieve_user_from_queue()
