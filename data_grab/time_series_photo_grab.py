import time
import threading
from threading import current_thread
import os

import user_manager as um
#import LoopedUserSearch is necessary here, otherwise gevent is not working, still don't know the reason
#from user_graph_constructor import LoopedUserSearch
import user_graph_constructor
import bfs_queue_manager as bqm
from pop_photo_grab import PhotoStream
from global_data import PHOTO_GRAB_INTERVAL

class TimeSeriesPhotoGrabber(object):
	def __init__(self):
		pass

	#photo processing is assigned with a new thread, avoid interferring with API requests 
	def _async_photo_processing(self):
		#start downloading photo stream
		ps = PhotoStream()
		ps.get_pop_photo_stream()
		#start parsing photo stream in another thread
		t = threading.Thread(target=ps.parse_photo_stream)
		t.start()		
		t.join()
		new_user_list = ps.get_new_user_list()
		#clear the list for next call
		ps.clear_new_user_list()
		self._add_to_user_search_queue(new_user_list)

	#after one run of photo grabbing, get the new authors of the popular photos and put to bfs queue
	def _add_to_user_search_queue(self, new_user_list):
		print new_user_list
		for user in new_user_list:
			if not um.user_seen(user):
				um.add_user(user)
				bqm.put_user(user)


#core function of the time series photo grabbing
def start_looping():
	pg = TimeSeriesPhotoGrabber()
	intervals = 0
	while True:
		count = 0
		pg._async_photo_processing()
		time.sleep(PHOTO_GRAB_INTERVAL)
		intervals += 1

		if intervals >= 1:
			break


