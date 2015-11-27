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


