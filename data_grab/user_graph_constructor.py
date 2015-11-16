import time
import multiprocessing
import os
import requests
import urllib
import urllib2

from multiprocessing import Process
from pxapi import api
from db_helper import mydb
from user_manager import UserManager
from bfs_queue_manager import BfsQueueManager
from global_data import CONSUMER_KEY, CONSUMER_SECRET
from proxy_manager import ProxyManager

class LoopedUserSearch(object):
	def __init__(self):
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)
		self.bm = BfsQueueManager()
		self.pm = ProxyManager()

	#the user mining process is an infinite loop
	def retrieve_user_from_queue(self):
		enter_time = time.time()

		# while True:
		# 	if not self.bm.is_empty():
		# 		user = self.bm.get_user()
		self._get_followers_of_user(9149967)
			#set break for test
			# if time.time() > enter_time+30:
			# 	break
			
	def _get_followers_of_user(self, user):
		um = UserManager()
		results = self.client.get_followers(user_id=str(6490074), rpp=100, full_format=1)
		
		follower_list = []
		count = 1
		for follower in results:
			if not um.user_seen(follower['id']):
				print "get %dth user" % count
				count+=1
				um.add_user(follower['id'])
				follower_list.append(follower)
				# self.bm.put_user(follower['id'])
		# print follower_list
		self._save_follower_relation_to_db(user, follower_list)

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
	p = Process(target=lus.retrieve_user_from_queue)
	p.start()
	p.join()
