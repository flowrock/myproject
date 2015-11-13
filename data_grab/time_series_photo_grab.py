import time
import threading

from user_graph_constructor import LoopedUserSearch
from bloom_user_check import MyBloomFilter
from pop_photo_grab import PhotoStream
from global_data import PHOTO_GRAB_INTERVAL, USER_AMOUNT, user_bfs_queue, bloom_filter

class TimeSeriesPhotoGrabber(object):
	def __init__(self):
		self.ps = PhotoStream()
		bloom_filter.clear_bloom_filter()
		self.intervals = 0
		self.unique_count = 0

	#photo processing is assigned with a new thread, avoid interferring with API requests 
	def _async_photo_processing(self):
		self.ps.get_pop_photo_stream()
		t = threading.Thread(target=self.ps.parse_photo_stream)
		t.start()		
		t.join()
		new_user_list = self.ps.get_new_user_list()
		#clear the list for next call
		self.ps.clear_new_user_list()
		self._add_to_user_search_queue(new_user_list)

	#core function of the time series photo grabbing
	def start_looping(self):
		while True:
			count = 0
			self._async_photo_processing()
			time.sleep(PHOTO_GRAB_INTERVAL)
			self.intervals += 1

			if self.intervals >= 1:
				break

	#after one run of photo grabbing, get the new authors of the popular photos and put to bfs queue
	def _add_to_user_search_queue(self, new_user_list):
		print new_user_list
		for user in new_user_list:
			if not bloom_filter.is_user_seen(user):
				self.unique_count += 1
				# print "Putting No.%d new user" % self.unique_count
				bloom_filter.add_user(user)
				user_bfs_queue.put(user)




