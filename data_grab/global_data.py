from Queue import Queue

#API key
CONSUMER_KEY = "evM04lzFCTjOLOO8V140JFbhnvxWFaI6H5Rz3mX5"
CONSUMER_SECRET = "U6NpXyxLVNzUExa5pwps5x8hsPdhbnfiuBCj4D0d"

#time interval between two photo grabs
PHOTO_GRAB_INTERVAL = 30
#popular photos to grab per time
PHOTO_GRAB_AMOUNT = 2

#define a task queue
global task_queue
task_queue = Queue()


