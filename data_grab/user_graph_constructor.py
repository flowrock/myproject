from gevent import monkey; monkey.patch_all()
import gevent
import multiprocessing
import requests
import pymongo
import time
import threading
from multiprocessing import Process, Pool
from Queue import Queue
from global_data import USER_AMOUNT
import user_manager

mydb = None
bfs_queue = None

#the user mining process is an infinite loop
def retrieve_user_from_queue():
    # start = time.time()
    connection = pymongo.MongoClient('localhost', 27017, maxPoolSize=10)
    global mydb
    mydb = connection.myproject
    threading_list = []
    for i in range(20):
        t = threading.Thread(target=start_loop)
        threading_list.append(t)
        time.sleep(1)
        t.start()
    for t in threading_list:
        t.join()

def start_loop():
    start = time.time()

    while True:
        if not bfs_queue.empty():
            user = bfs_queue.get()
            print user
            _request_followers_of_user(user)
        if time.time()-start > 300:
            break

def _request_followers_of_user(user):
    url = 'https://api.500px.com/v1/users/'+str(user)+'/followers?fullformat=1&rpp=100'
    total_pages = _fetch(user, url, 1, 0)
    if total_pages is not None and total_pages > 1:
        jobs = []
        for page in xrange(2,total_pages+1):
            jobs.append(gevent.spawn(_fetch, user, url+"&page="+str(page), page, 0))
        gevent.joinall(jobs)
    else:
        bfs_queue.put(user)
        
def _fetch(user, url, page, attempts):
    pages = None
    followers = None
    result = None
    if attempts >= 3:
        return None
    try:
        response = requests.get(url,timeout=3)
        result = response.json()
        # print "successful getting page %d"%page
        followers = result['followers']
        follower_list = []   
        for follower in followers:
            follower_list.append(follower)
        _save_follower_relation_to_db(user, follower_list) 
    except Exception, e:
        # print e
        # print "refetch page %d"%page
        return _fetch(user, url, page, attempts+1)
    return result['followers_pages']

#may want to spawn to separate threads
def _save_follower_relation_to_db(user, follower_list):
    follower_id_list = []

    #save users into users collection
    user_collection = mydb.users
    for follower in follower_list:
        follower_id_list.append(follower['id'])
        if not user_manager.user_seen(follower['id']):
            user_manager.add_user(follower['id'])
            bfs_queue.put(follower['id'])
            follower['following'] = [user]
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

    retrieve_user_from_queue()
