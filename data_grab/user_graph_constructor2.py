from gevent import monkey; monkey.patch_all()
import gevent
import multiprocessing
import requests
import time
import threading
from Queue import Queue
import user_manager
from db_helper import mydb
from global_data import THREAD_NUM

bfs_queue = None

count = 1

#the user mining process is an infinite loop
def retrieve_user_from_queue():
    threading_list = []
    for i in range(THREAD_NUM):
        t = threading.Thread(target=start_loop)
        threading_list.append(t)
        t.start()
        time.sleep(1)
    for t in threading_list:
        t.join()

def start_loop():
    start = time.time()
    while True:
        if not bfs_queue.empty():
            user = bfs_queue.get()
            global count
            print count
            count+=1
            _request_followers_of_user(user)
        else:
            time.sleep(1)
        # if time.time()-start > 60:
        #     break

def _request_followers_of_user(user):
    url = 'https://api.500px.com/v1/users/'+str(user)+'/followers?fullformat=1&rpp=100'
    global proxy_manager
    total_pages, l1 = _fetch(url, 1, 0)
    if total_pages is not None and l1 is not None:
        value = []
        for f in l1:
            value.append(f)
        if total_pages > 1:
            jobs = []
            for page in xrange(2,total_pages+1):
                jobs.append(gevent.spawn(_fetch, url+"&page="+str(page), page, 0))
            gevent.joinall(jobs)
            for job in jobs:
                r = job.value
                if r[1] is not None:
                    for fv in r[1]:
                        value.append(fv)
        if len(value) > 0:
            _save_follower_relation_to_db(user, value)
    else:
        bfs_queue.put(user)

        
def _fetch(url, page, attempts):
    pages = None
    followers = None
    result = None
    if attempts >= 3:
        return None, None
    try:
        response = requests.get(url, timeout = 3)
        result = response.json()
        followers = result['followers']
        pages = result['followers_pages']
    except Exception, e:
        return _fetch(url, page, attempts+1)
    return pages, followers


def _save_follower_relation_to_db(user, follower_list):
    follower_id_list = []
    refined_follower_list = []
    rejected_fields = ['domain','firstname','lastname','cover_url','thumbnail_background_url','avatars']

    for follower in follower_list:
        follower_id_list.append(follower['id'])
        if not user_manager.user_seen(follower['id']):
            user_manager.add_user(follower['id'])
            bfs_queue.put(follower['id'])
            for field in rejected_fields:
                follower.pop(field, None)
            refined_follower_list.append(follower)

    #save users into users collection
    user_collection = mydb.users
    if len(refined_follower_list)>0:
        user_collection.insert_many(refined_follower_list)

    #add the following relation of the given user into user relation collection
    user_relation_collection = mydb.user_relation
    relation = {}
    relation['user'] = user
    relation['followers'] = follower_id_list
    user_relation_collection.insert(relation)


def user_search_start_running():
    global bfs_queue
    bfs_queue = Queue(maxsize=0)
    bfs_queue.put(9149967)

    retrieve_user_from_queue()
