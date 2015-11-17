from gevent import monkey; monkey.patch_all()
import gevent
import multiprocessing
import requests


from multiprocessing import Process
from db_helper import mydb
from user_manager import UserManager
from bfs_queue_manager import BfsQueueManager
from global_data import CONSUMER_KEY, CONSUMER_SECRET
from proxy_manager import ProxyManager

class LoopedUserSearch(object):
    def __init__(self):
        self.bm = BfsQueueManager()
        self.pm = ProxyManager()

    #the user mining process is an infinite loop
    def retrieve_user_from_queue(self):
        # while True:
        #   if not self.bm.is_empty():
        #       user = self.bm.get_user()
        #       self._get_followers_of_user(user)
        self._get_followers_of_user(6490074)

            
    def _get_followers_of_user(self, user):
        um = UserManager()
        results = self._request_followers_of_user(user)
        follower_list = []

        for page in results:
            try:
                for follower in page['followers']:
                    if not um.user_seen(follower['id']):
                        um.add_user(follower['id'])
                        follower_list.append(follower)
            except Exception, e:
                pass
                # self.bm.put_user(follower['id'])
        # print follower_list
        self._save_follower_relation_to_db(user, follower_list)

    def _request_followers_of_user(self, user):
        url = 'https://api.500px.com/v1/users/'+str(user)+'/followers?fullformat=1&rpp=100'
        first_page = self._fetch(1, url+"&page=1", 0)
        total_pages = first_page['followers_pages']
        results = []
        results.append(first_page)
        if total_pages is not None and total_pages > 1:
            jobs = []
            for page in xrange(2,total_pages+1):
                jobs.append(gevent.spawn(self._fetch, page, url+"&page="+str(page), 0))
            gevent.joinall(jobs)
            for job in jobs:
                results.append(job.value)
        return results

    def _fetch(self, page, url, attempt_num):
        status = None
        result = None
        followers = None
        #define the maximum connection attempts, if reached, break  
        if attempt_num >= 4:
            return None
        try :
            response = requests.get(url,timeout=3)
            status = response.status_code
            result = response.json()
            followers = result['followers']
        except Exception, e :
            # print "reconnect %dth page"%page
            return self._fetch(page,url, attempt_num+1)
            
        if followers is None:
            return self._fetch(page,url,attempt_num+1)
        # print "get %dth page"%page
        return result   


    #may want to spawn to separate threads
    def _save_follower_relation_to_db(self, user, follower_list):
        follower_id_list = []

        #save users into users collection
        user_collection = mydb.users
        for follower in follower_list:
            user_collection.insert(follower)
            follower_id_list.append(follower['id'])

        #add the following relation of the given user into user relation collection
        user_relation_collection = mydb.user_relation
        relation = {}
        relation['user'] = user
        relation['followers'] = follower_id_list
        user_relation_collection.insert(relation)


def user_search_start_running():
    lus = LoopedUserSearch()
    # pool = multiprocessing.Pool(processes=5)
    # for p in xrange(5):
    #     pool.apply_async(lus.retrieve_user_from_queue)
    # pool.close()
    # pool.join()
    lus.retrieve_user_from_queue()
