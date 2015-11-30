from Queue import Queue
import api
import operator
import requests
import time
from multiprocessing import Process, Queue
from nltk.tag import StanfordNERTagger

import global_data
from global_data import CONSUMER_KEY, CONSUMER_SECRET, PHOTO_GRAB_PER_TIME, PHOTO_CATEGORIES, GEONAME_ACCOUNTS, EXCLUDED_LOCATIONS
from db_helper import mydb
import photo_manager
import location_manager

class PhotoStream(object):
	def __init__(self):
		self.client = api.FiveHundredPx(CONSUMER_KEY, CONSUMER_SECRET)
		self.store_list= []
		self.st = StanfordNERTagger(r'english.all.3class.nodistsim.crf.ser.gz',r'stanford-ner.jar')

	def request_pop_photo_stream(self, category, attempts):
		if attempts == 3:
			return None
		results = None
		try:
			results = self.client.get_photos(rpp=10, feature='popular', only=category, sort='rating', tags=1)
		except:
			self.request_pop_photo_stream(category, attempts+1)
		return results

	def get_located_photos(self, photo_list, category):	
		for photo in photo_list:
			if photo_manager.photo_seen(photo['id']):
				self.store_list.append(photo)
			else:
				photo_manager.add_photo(photo['id'])
				if photo['latitude'] is not None:
					photo['exact location'] = True
					self.store_list.append(photo)
				elif category != 'People':
					self.extract_location(photo,category)				
		return self.store_list

	def extract_location(self, photo, category):
		tags = photo['tags']
		possible_locations = []
		q = Queue()
		job_list = []
		for tag in tags:
			tag = tag.title()
			if tag in location_manager.known_locations:
				possible_locations.add(tag)
			elif tag in location_manager.not_locations:
				continue
			elif tag not in EXCLUDED_LOCATIONS:
				p = Process(target=self.nlp_analyze, args=(tag,q))
				job_list.append(p)
				p.start()
		for job in job_list:
			job.join()
		while not q.empty():
			possible_locations.extend(q.get())

		if len(possible_locations) == 0:
			return None
		location_dic = {}
		for i in range(len(possible_locations)):
			if possible_locations[i] in location_dic:
				location_dic[possible_locations[i]] = location_dic[possible_locations[i]]+1
			else:
				location_dic[possible_locations[i]] = 1
		sorted_location = sorted(location_dic.items(),key=operator.itemgetter(1))
		sorted_location.reverse()
		#use the location most frequently appeared in tags
		location = sorted_location[0]
		print photo['name']
		print location[0]
		print "\n"
		lat, lng = self.request_latlng(location[0], category)
		if lat is not None:
			photo['latitude'] = lat
			photo['longitude'] = lng
			photo['exact location'] = False
			self.store_list.append(photo)

	def nlp_analyze(self, text, q):
		if text is None or text == "":
			return []
		possible_locations = []
		result = self.st.tag(text.split())
		loc_tmp = ""
		conseq = False
		for r in result:
			if r[1] == 'LOCATION':
				if conseq:
					loc_tmp = loc_tmp+' '+r[0]
				else:
					loc_tmp = r[0]
					conseq = True
			else:
				if loc_tmp != "":
					location_manager.known_locations.add(loc_tmp)
					possible_locations.append(loc_tmp)
				loc_tmp = ""
				conseq = False
				location_manager.not_locations.add(r[0])
		if loc_tmp != "":
			possible_locations.append(loc_tmp)
		q.put(possible_locations)

	def request_latlng(self, location, category):
		#use three geonames.org accounts to avoid requesting limitations
		geoname_account = GEONAME_ACCOUNTS[PHOTO_CATEGORIES.index(category)]
		payload = {'q':location,'maxRows':1,'username':geoname_account}
		try:
			response = requests.get('http://api.geonames.org/searchJSON', params=payload)
			result = response.json()
			return float(result['geonames'][0]['lat']), float(result['geonames'][0]['lng'])
		except:
			return None, None
		
	def save_photo_stream_to_db(self, photo_list, category):
		if category == 'City and Architecture':
			photo_collection = mydb.city
		elif category == 'Landscapes':
			photo_collection = mydb.landscape
		elif category == 'People':
			photo_collection = mydb.people
		for photo in photo_list:
			#check if the photo is already in the database
			if photo_collection.find_one({'id':photo['id']}) is None:
				if photo['latitude'] is not None:
					photo_collection.insert(photo)
			else:
				photo_collection.update_one({'id':photo['id']},{
	        		"$set": {
	            	"rating": photo['rating']
	        		},
	        		"$currentDate": {"lastModified": True}
	    			}
				)


