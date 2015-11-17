import user_manager

def test():
	user_manager.clear_all()
	print user_manager.user_seen(5)
	user_manager.add_user(5)
	print user_manager.user_seen(5)

test()
