import threading
import time
from global_data import user_bfs_queue

#the whole user_graph construction needs be done using a separate thread
# class UserGraph(object):
# 	def __init__(self):

class LoopedUserSearch(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.unique_count = 0

	def run(self):
		while True:
			if not user_bfs_queue.empty():
				# print user_bfs_queue.qsize()
				self.unique_count+=1
				print "Getting No.%d user" % self.unique_count
				print user_bfs_queue.get(0)
			

