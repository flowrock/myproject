from multiprocessing import Queue

_bfs_queue = Queue()

class BfsQueueManager(object):	
	def put_user(self, user_id):
		_bfs_queue.put(user_id)

	def get_user(self):
		return _bfs_queue.get()

	def is_empty(self):
		return _bfs_queue.empty()