from multiprocessing.dummy import Pool as ThreadPool
from time_series_photo_grab import TimeSeriesPhotoGrabber
from user_graph_constructor import LoopedUserSearch

def execute():
	photo_grabber = TimeSeriesPhotoGrabber()
	user_searcher = LoopedUserSearch()

	pool = ThreadPool(2)
	pool.apply_async(user_searcher.retrieve_user_from_queue)
	photo_grabber.start_looping()
	pool.close()
	pool.join()

if __name__ == '__main__':
	execute()