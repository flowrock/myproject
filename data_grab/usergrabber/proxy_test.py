from proxy_manager import ProxyManager
import proxy_manager
import threading
import time

pm = ProxyManager()
pm.retrieve_new_proxies()
while True:
	if len(pm.proxy_list)==0:
		print "wait a minute"
		time.sleep(3)
	else:
		break
print pm.proxy_list
