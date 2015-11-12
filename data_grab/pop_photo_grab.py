import sys
import datetime
import time

from photo import api
from pprint import pprint

from global_data import CONSUMER_KEY, CONSUMER_SECRET, PHOTO_GRAB_INTERVAL, PHOTO_GRAB_AMOUNT

class PhotoStream(object):
	def __init__(self):
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)

	def get_time_series_pop_photo_stream(self):
		interval = 0
		while True:
			count = 0
			results = self.client.get_photos(rpp=100, feature='popular')
			for photo in results:
				print photo
				count += 1
				if count==PHOTO_GRAB_AMOUNT:
					break
			print '************************'
			print '\n'
			print '\n'
			time.sleep(PHOTO_GRAB_INTERVAL)
			interval += 1

			if interval >= 3:
				break


			
