from multiprocessing.dummy import Pool as ThreadPool
from time_series_photo_grab import TimeSeriesPhotoGrabber
from user_graph_constructor import LoopedUserSearch
from global_data import bloom_filter, user_bfs_queue

import time

def execute():
	#photo_grabber = TimeSeriesPhotoGrabber()
	user_searcher = LoopedUserSearch()

	#photo_grabber.start_looping()

	pool = ThreadPool(2)
	#time.sleep(5)
	pool.apply_async(user_searcher.retrieve_user_from_queue)
	pool.close()
	pool.join()

if __name__ == '__main__':
	execute()