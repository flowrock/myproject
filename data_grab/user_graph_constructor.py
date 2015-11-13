import urllib2

from pxapi import api
from global_data import CONSUMER_KEY, CONSUMER_SECRET, user_bfs_queue

class LoopedUserSearch(object):
	def __init__(self):
		self.unique_count = 0
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)

	#the user mining process is an infinite loop
	def retrieve_user_from_queue(self):
		while True:
			if not user_bfs_queue.empty():
				# print user_bfs_queue.qsize()
				self.unique_count += 1
				# print "Getting No.%d user" % self.unique_count
				user = user_bfs_queue.get()
				self.get_followers_of_user(user)
			
	def get_followers_of_user(self, user):
		results = self.client.get_followers(user_id=str(user), rpp=100, full_format=1)
		count = 1
		for follower in results:
			print "%dth follower" % count
			print follower['username']
			count += 1
		
