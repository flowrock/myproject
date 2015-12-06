from flask import Flask, request
import pymongo
import json

app = Flask(__name__)
connection = pymongo.MongoClient('localhost', 27017, maxPoolSize=10)
mydb = connection.px500

@app.route("/api/photos")
def get_photos():
	day = 1 #default photos shown for the lastest day
	category = 'all' #default category is all categories
	if ('day' in request.args):
		day = request.args.get('day')
	if ('category' in request.args):
		category = request.args.get('category')

	item = mydb.current.find_one({'category':category, 'day':int(day)})
	return json.dumps(item['photos'])
	

if __name__ == '__main__':
	app.run()
