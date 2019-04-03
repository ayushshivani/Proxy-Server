import base64
import copy
import _thread as thread
import socket
import sys
import os
import datetime
import time
import json
import threading
import email.utils as eut


max_connections = 10
CACHE_DIR = "./cache"
BLACKLIST_FILE = "blacklist.txt"
USERNAME_PASSWORD_FILE = "username_password.txt"
MAX_CACHE_BUFFER = 3
NO_OF_OCC_FOR_CACHE = 2
blocked = []
admins = []
BUFFER_SIZE = 1024
buf_size = 1024

class Proxy_Server():
	
	def Request_handler(client_socket,client_addr,client_data):
	
		info = make_info(client_addr, client_data)
		if not info:
			print("no any info")
			client_socket.close()
			return
		
		isb = is_blocked(client_socket, client_addr, details)
		if isb:
			print("Block status : ", isb)
			client_socket.send("HTTP/1.0 200 OK\r\n")
			client_socket.send("Content-Length: 11\r\n")
			client_socket.send("\r\n")
			client_socket.send("Error\r\n")
			client_socket.send("\r\n\r\n")


		elif info["method"] == "GET":
		    info = get_cache_info(client_addr, info)
		    if info["last_mtime"]:
		        info = insert_if_modified(info)
		    serve_get(client_socket, client_addr, info)

		elif info["method"] == "POST":
		    serve_post(client_socket, client_addr, info)

		client_socket.close()

		print (client_addr + "closed")

	def __init__(self):
		
		Sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		Sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		Sock_server.bind(('', 20000))
		Sock_server.listen(5)
		  
		hostname=str(Sock_server.getsockname()[0])
		portnum=str(Sock_server.getsockname()[1])

		print ("proxy server running on " + hostname + " port "  + portnum) 

		while True:
		    try:
		        Sock_client , Addr_client=Sock_server.accept()
		        
		        Data_client=Sock_client.recv(1024)

		        a="".join(map(chr, Data_client))
		        b=a.split(' ')
		        print(b)

		        thread.start_new_thread(Request_handler,(Sock_client,Addr_client,b))

		    except KeyboardInterrupt:
		        Sock_client.close()
		        Sock_server.close()
		        break




	# def if_blocked(client_socket,client_addr,details):

		
	# 	if details["auth_b64"] in admins:
	# 		return False
	# 	if not (details["server_url"] + ":" + str(details["server_port"])) in blocked:
	# 		return False

	# 	if not details["auth_b64"]:
	# 		return True

	# 	return True

	
	def serve_post(client_socket,client_addr,details):
		
		try:
			server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			server_socket.connect((details["server_url"], details["server_port"]))
			server_socket.send(details["client_data"])

			while True:
				reply = server_socket.recv(buf_size)
				if len(reply):
					client_socket.send(reply)
				else:
					break

			server_socket.close()
			client_socket.close()
			return

		except Exception as e:
			server_socket.close()
			client_socket.close()
			print(e)
			return


	def serve_get(client_socket, client_addr, info):
	    try:
	        
	        client_data = info["client_data"]
	        do_cache = info["do_cache"]
	        cache_path = info["cache_path"]
	        last_mtime = info["last_mtime"]

	        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	        proxy_socket.connect((info["server_url"], info["server_port"]))
	        proxy_socket.send(info["client_data"])

	        reply_server = proxy_socket.recv(BUFFER_SIZE)
	        checkstr = "304 Not Modified"
	        
	        if last_mtime and checkstr in reply_server:
	            prs="returning cached file " + cache_path + " to " + str(client_addr)
	            print(prs)
	            aux_send(cache_path,client_socket,info)
	        
	        else:
	            if do_cache:
	            	prs="caching file " + cache_path + " to " + str(client_addr)
	            	print(prs)
	            	modify_cache()
	            	mutex_lock(info["total_url"])
	            	f = open(cache_path, "w+")
	            	while len(reply_server):
	            		client_socket.send(reply_server)
	            		f.write(reply_server)
	            		reply_server = proxy_socket.recv(BUFFER_SIZE)
	            	f.close()
	            	mutex_unlock(info["total_url"])
	            	client_socket.send("\r\n\r\n")
	            else:
	            	prs="without caching sending file " + cache_path + " to " + str(client_addr)
	            	print(prs)
	            	while len(reply_server):
	            		client_socket.send(reply_server)
	            		reply_server = proxy_socket.recv(BUFFER_SIZE)
	            	client_socket.send("\r\n\r\n")
	        proxy_socket.close()
	        client_socket.close()
	        return

	    except Exception as e:
	        proxy_socket.close()
	        client_socket.close()
	        print(e)
	        return


	def mutex_lock(file):
	    if file not in locks:
	        lock = threading.Lock()
	        locks[file] = lock
	    else:
	        lock = locks[file]
	    lock.acquire()

	def mutex_unlock(file):
		lock = locks[file]
		lock.release()




	def make_info(client_addr, client_data):

	    url = client_data[1]

	    colon = url.find("://")
	    if colon != -1:
	        protocol = url[:colon]
	        url = url[(colon+3):]
	    else:
	        protocol = "http"

	    port_pos = url.find(":")
	    path_pos = url.find("/")
	    server_url = url[:path_pos]
	    server_port = 80

	    if path_pos == -1:
	        path_pos = len(url)
	    
	    if port_pos>=0 and port_pos <= path_pos:
	        server_port = int(url[(port_pos+1):path_pos])
	        server_url = url[0:port_pos]

	    # auth_line = [ line for line in lines if "Authorization" in line]
	    # if len(auth_line):
	    #     auth_b64 = auth_line[0].split()[2]
	    # else:
	    #     auth_b64 = None

	    return
	    {
	        "protocol" : protocol,
	        "method" : client_data[0],
	        "auth_b64" : auth_b64,
	        "total_url" : url,
	        "server_url" : server_url,
	        "server_port" : server_port,
	        "client_data" : client_data,
	    }

	def is_blocked(client_socket, client_addr, info):

	    if not (info["server_url"] + ":" + str(info["server_port"])) in blocked:
	        return False
	    if not info["auth_b64"]:
	        return True
	    if info["auth_b64"] in admins:
	        return False
	    return True

	def cache_status(file):
	    
	    prev_mtime=None
	    path = "./cache" + "/" + file.replace("/", "??")
	    if os.path.isfile(path):
	        prev_mtime = time.strptime(time.ctime(os.path.getmtime(path)), "%a %b %d %H:%M:%S %Y")
	    
	    return path, prev_mtime


	def record_info(file, client_addr):
	    file = file.replace("/", "??")
	    if not file in logs:
	        logs[file] = []
	    DATE = time.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
	    logs[file].append
	    (
	    	{
	            "datetime" : DATE,
	            "client" : json.dumps(client_addr),
	     	}
	    )
	    log_arr = logs[file.replace("/", "??")]
	    if len(log_arr) < 3 :
	    	return False
	    oldest_time = datetime.datetime.fromtimestamp(time.mktime(log_arr[len(log_arr)-3]["datetime"]))
	    delta_time  = datetime.timedelta(minutes=5)
	    curr_time   = datetime.datetime.now()
	    
	    if  curr_time > oldest +delta :
	        return False
	    else:
	    	return True


	def get_cache_info(client_addr, info):
	    mutex_lock(info["total_url"])
	   
	    info["do_cache"] = record_info(info["total_url"], client_addr)
	    
	    info["cache_path"], info["last_mtime"] = cache_status(info["total_url"])
	    
	    mutex_unlock(info["total_url"])
	    
	    return info


	def insert_if_modified(details):

	    lines = details["client_data"].splitlines()
	    while lines[len(lines)-1] == '':
	        lines.remove('')

	    #header = "If-Modified-Since: " + time.strptime("%a %b %d %H:%M:%S %Y", details["last_mtime"])
	    header = time.strftime("%a %b %d %H:%M:%S %Y", details["last_mtime"])
	    header = "If-Modified-Since: " + header
	    lines.append(header)

	    details["client_data"] = "\r\n".join(lines) + "\r\n\r\n"

	    return details

	def aux_send(cache_path,client_socket,info):
		mutex_lock(info["total_url"])
		
		f = open(cache_path, 'rb')
		chunk = f.read(BUFFER_SIZE)
		while chunk:
			client_socket.send(chunk)
			chunk = f.read(BUFFER_SIZE)
		f.close()
		mutex_unlock(info["total_url"])


	def modify_cache():
	    cache_files = os.listdir(CACHE_DIR)
	    
	    if len(cache_files) < 3:
	        return
	    
	    for file in cache_files:
	        mutex_lock(file)

	    last_mtime = min(logs[file][-1]["datetime"] for file in cache_files)
	    file_to_del = [file for file in cache_files if logs[file][-1]["datetime"] == last_mtime][0]
	    os.remove(CACHE_DIR + "/" + file_to_del)
	    
	    for file in cache_files:
	        mutex_unlock(file)
















if __name__ == "__main__":
	
	if len(sys.argv) != 2:
	    print ("Usage: python %s <PROXY_PORT>" % sys.argv[0])
	    print ("Example: python %s 20000" % sys.argv[0])
	    raise SystemExit

	try:
		proxy_port = int(sys.argv[1])
	except:
		print("Problem in port number")
		raise(SystemExit)

	if not os.path.isdir(CACHE_DIR):
		os.makedirs(CACHE_DIR)

	fr = open(BLACKLIST_FILE, "rb")
	black_list = ""
	while True:
		buff = fr.read()
		if len(buff):
			black_list += str(buff)
		else:
			break
	fr.close()
	black_list = black_list.splitlines()

	fr = open(USERNAME_PASSWORD_FILE,"rb")
	data = ""
	while True:
		chunk = fr.read()
		if not len(chunk):
			break
		data += str(chunk)
	fr.close() 


	for lt in black_list:
		admins.append(base64.b64encode(bytes(lt,'utf-8')))

	for file in os.listdir(CACHE_DIR):
		os.remove(CACHE_DIR + "/" + file)
		

	Proxy_Server()



