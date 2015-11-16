import time_series_photo_grab as photo_grabber
import user_graph_constructor as user_graph
import proxy_manager
import time

def execute():
	#proxy_manager.refresh_proxies()
	user_graph.user_search_start_running()
	photo_grabber.start_looping()

if __name__ == '__main__':
	execute()