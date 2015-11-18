from gevent import monkey; monkey.patch_all()
import gevent
# from gevent.queue import Queue
import multiprocessing
import requests
import pymongo
import time
import threading
from multiprocessing import Process, Pool
# from Queue import Queue
from global_data import USER_AMOUNT
import user_manager
import bfs_queue_manager 

class UserSearcher(Process):
    def __init__(self):
        Process.__init__(self)
        connection = pymongo.MongoClient('localhost', 27017, maxPoolSize=10, connect=False)
        self.mydb = connection.myproject
    def run(self):
        self.retrieve_user_from_queue()
    #the user mining process is an infinite loop
    def retrieve_user_from_queue(self):
        start = time.time()
        threading_list = []
        for i in range(5):
            t = threading.Thread(target=self.start_loop)
            threading_list.append(t)
            t.start()
            time.sleep(1)
        for t in threading_list:
            t.join()
        # self.start_loop()

    def start_loop(self):
        start = time.time()
        print "start loop"
        while True:
            if not bfs_queue_manager.is_empty():
                user = bfs_queue_manager.get_user()
                print user
                self._request_followers_of_user(user)
            else:
                time.sleep(1)
            if time.time()-start > 300:
                break

    def _request_followers_of_user(self, user):
        url = 'https://api.500px.com/v1/users/'+str(user)+'/followers?fullformat=1&rpp=100'
        total_pages = self._fetch(user, url, 1, 0)
        if total_pages is not None and total_pages > 1:
            jobs = []
            for page in xrange(2,total_pages+1):
                jobs.append(gevent.spawn(self._fetch, user, url+"&page="+str(page), page, 0))
            gevent.joinall(jobs)
        else:
            bfs_queue_manager.put_user(user)
            
    def _fetch(self, user, url, page, attempts):
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
            self._save_follower_relation_to_db(user, follower_list) 
        except Exception, e:
            # print e
            # print "refetch page %d"%page
            return self._fetch(user, url, page, attempts+1)
        return result['followers_pages']

    #may want to spawn to separate threads
    def _save_follower_relation_to_db(self, user, follower_list):
        follower_id_list = []

        #save users into users collection
        user_collection = self.mydb.users
        for follower in follower_list:
            follower_id_list.append(follower['id'])
            if not user_manager.user_seen(follower['id']):
                user_manager.add_user(follower['id'])
                bfs_queue_manager.put_user(follower['id'])
                follower['following'] = [user]
                user_collection.insert(follower)
            else:
                record = user_collection.find_one({'id':follower['id']})
                record['following'].append(user)
                user_collection.save(record)

        #add the following relation of the given user into user relation collection
        user_relation_collection = self.mydb.user_relation
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
    bfs_queue_manager.put_user(9149967)
    for i in range(5):
        w = UserSearcher()
        w.start()
        time.sleep(1)
    
    # retrieve_user_from_queue()
