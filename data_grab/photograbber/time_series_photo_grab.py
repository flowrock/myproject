import time
import threading

from pop_photo_grab import PhotoStream
from global_data import PHOTO_GRAB_INTERVAL

class TimeSeriesPhotoGrabber(object):
	def __init__(self):
		pass

	#photo processing is assigned with a new thread, avoid interferring with API requests 
	def _async_photo_processing(self):
		#start downloading photo stream
		ps = PhotoStream()
		categories = ['City and Architecture','Landscapes','People']
		for cat in categories:
			ps.get_pop_photo_stream(cat)
		#start parsing photo stream in another thread
		ps.parse_photo_stream()
		ps.save_photo_stream_to_db()

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


