from gevent.queue import Queue

bfs_queue = Queue()

def put_user(user_id):
	bfs_queue.put(user_id)

def get_user():
	return bfs_queue.get()

def is_empty():
	return bfs_queue.empty()