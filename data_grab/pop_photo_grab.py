import sys
import datetime
import time
from fivehundredpx.client import FiveHundredPXAPI

def get_time_series_pop_photo_stream(api_func, mongodb_name, mongodb_coll, secs_per_interval=60, 
	max_intervals=3, **mongo_conn_kw):

	interval = 0
	while True:
		now = str(datetime.datetime.now()).split(".")[0]
		ids = save_to_mongo(api_func(),mongodb_name,mongodb_coll+"-"+now)
		print >> sys.stderr, "Write {0} trends".format(len(ids))
		print >> sys.stderr, "Zzz..."
		print >> sys.stderr.flush()

		time.sleep(secs_per_interval)
		interval += 1

		if interval >= 3:
			break
			
