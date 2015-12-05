from flask import Flask, request, jsonify, make_response
import photo_manager

import threading

app = Flask(__name__)

@app.route("/api/photos")
def get_photos():
	day = 1 #default photos shown for the lastest day
	category = 'all' #default category is all categories
	day = request.args.get('day')
	category = request.args.get('category')

	response = photo_manager.get_requested_photos(category, int(day))
	return response
	# if response is not None:
	# 	response.status_code = 200
	# 	return response
	# else:
	# 	return not_found()
	# return "hello"

@app.errorhandler(404)
def not_found():
	return make_response(jsonify({'error':'Not found'}), 404)

if __name__ == '__main__':
	t = threading.Thread(target=photo_manager.start_photo_managing)
	t.start()
	app.run()
