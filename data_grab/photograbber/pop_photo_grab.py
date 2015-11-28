from Queue import Queue
import api
import operator
from nltk.tag import StanfordNERTagger

import global_data
from global_data import CONSUMER_KEY, CONSUMER_SECRET, PHOTO_GRAB_PER_TIME
from db_helper import mydb

class PhotoStream(object):
	def __init__(self):
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)
		self.location_given_list = []
		self.location_not_given_list = []
		self.st = StanfordNERTagger(r'english.all.3class.nodistsim.crf.ser.gz',r'stanford-ner.jar')

	def get_pop_photo_stream(self, category):
		photo_list = []
		try:
			results = self.client.get_photos(rpp=100, feature='popular', only=category, sort=rating, tags=1)
		except Exception, e:
			return self.get_pop_photo(category)
		for photo in results:
			photo_list.append(photo)
		return photo_list

	def parse_photo_stream(self, photo_list, category):
		for photo in photo_list:
			if photo['latitude'] is not None:
				self.location_given_list.append(photo)
			else:
				name = photo['name']
				disc = photo['description']
				tags = photo['tags']
				rn = st.tag(name.split())
				rd = st.tag(disc.split())
				rt = []
				for t in tags:
					t = t.title()
					rt.append(st.tag(t.split()))
				possible_locations = []
				for n in rn:
					if n[1] == 'LOCATIONS':
						possible_locations.append(n[0])
				for d in rd:
					if d[1] == 'LOCATIONS':
						possible_locations.append(d[0])
				for tt in rt:
					if tt[1] == 'LOCATIONS':
						possible_locations.append(tt[0])
				if len(possible_locations) == 0:
					continue
				location_dic = {}
				for i in range(len(possible_locations)):
					if possible_locations[i] in location_dic:
						location_dic[possible_locations[i]] = location_dic[possible_locations[i]]+1
					else:
						location_dic[possible_locations[i]] = 1
				sorted_location = sorted(location_dic.items(),key=operator.itemgetter(1))
				sorted_location.reverse()
				print sorted_location[0]

		
	def save_photo_stream_to_db(self):
		#save popular photos into photos collection
		photo_collection = mydb.photos
		#check if the photo exists
		photo_check = photo_collection.find_one({'id':photo['id']})
		#photo has not seen before, insert
		if photo_check is None:
			photo_collection.insert(photo)
		#has seen, update time varying fields
		else:
			photo_collection.update({'id':photo['id']},photo)










