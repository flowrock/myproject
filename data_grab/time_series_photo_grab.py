import time
import threading

from user_graph_constructor import LoopedUserSearch
from bloom_user_check import MyBloomFilter
from pop_photo_grab import PhotoStream
from global_data import PHOTO_GRAB_INTERVAL, USER_AMOUNT, user_bfs_queue

class TimeSeriesPhotoGrabber(object):
	def __init__(self):
		self.ps = PhotoStream()
		self.bf = MyBloomFilter(capacity=USER_AMOUNT, error_rate=0.01)
		self.bf.clear_bloom_filter()
		self.intervals = 0
		self.unique_count = 0

	#photo processing is assigned with a new thread, avoid interferring with API requests 
	def async_photo_processing(self):
		self.ps.get_pop_photo_stream()
		t = threading.Thread(target=self.ps.parse_photo_stream)
		t.start()		
		t.join()
		new_user_list = self.ps.get_new_user_list()
		self.ps.clear_new_user_list()
		self.add_to_user_search_queue(new_user_list)

	#core function of the time series photo grabbing
	def start_looping(self):
		while True:
			count = 0
			self.async_photo_processing()
			time.sleep(PHOTO_GRAB_INTERVAL)
			self.intervals += 1

			if self.intervals >= 1:
				break
	#after one run of photo grabbing, get the new authors of the popular photos and put to bfs queue
	def add_to_user_search_queue(self, new_user_list):
		print new_user_list
		for user in new_user_list:
			if not self.bf.is_user_seen(user):
				self.unique_count += 1
				# print "Putting No.%d new user" % self.unique_count
				self.bf.add_user(user)
				user_bfs_queue.put(user)




