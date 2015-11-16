from proxy_manager import ProxyManager
import proxy_manager
import threading
import time

pm = ProxyManager()
proxy_manager.refresh_proxies()
while True:
	if len(pm.current_available_proxies())==0:
		print "wait a minute"
		time.sleep(3)
	else:
		break
print pm.current_available_proxies()
