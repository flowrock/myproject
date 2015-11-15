from bitarray import bitarray
from global_data import USER_AMOUNT

_user_bit_array = bitarray(USER_AMOUNT)

class UserManager(object):
	def user_seen(self, user_id):
		return _user_bit_array[user_id]

	def add_user(self, user_id):
		_user_bit_array[user_id] = 1

	def clear_all(self):
		_user_bit_array.setall(False)