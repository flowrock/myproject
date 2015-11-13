from Queue import Queue

#API key
CONSUMER_KEY = "evM04lzFCTjOLOO8V140JFbhnvxWFaI6H5Rz3mX5"
CONSUMER_SECRET = "U6NpXyxLVNzUExa5pwps5x8hsPdhbnfiuBCj4D0d"

#time interval between two photo grabs
PHOTO_GRAB_INTERVAL = 10
#popular photos to grab per time
PHOTO_GRAB_PER_TIME = 1

#estimated user number
USER_AMOUNT = 100000000

#define user queue for bfs search
user_bfs_queue = Queue()




