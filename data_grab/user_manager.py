from bitarray import bitarray
from global_data import USER_AMOUNT

user_bit_array = bitarray(USER_AMOUNT)

def user_seen(user_id):
	return user_bit_array[user_id]

def add_user(user_id):
	user_bit_array[user_id] = 1

def clear_all():
	user_bit_array.setall(False)