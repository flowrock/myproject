from pybloomfilter import BloomFilter

class MyBloomFilter(object):
	def __init__(self, capacity, error_rate):
		self.bf = BloomFilter(capacity, error_rate, 'user.bloom')

	def is_user_seen(self, user_id):
		return user_id in self.bf
	
	def add_user(self, user_id):
		self.bf.add(user_id)

	def clear_bloom_filter(self):
		self.bf.clear_all()

