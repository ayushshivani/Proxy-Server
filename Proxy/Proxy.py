import socket 
import threading
import _thread as thread
import os

def is_blocked(client_socket, client_addr, details):

    if not (details["server_url"] + ":" + str(details["server_port"])) in blocked:
        return False
    if not details["auth_b64"]:
        return True
    if details["auth_b64"] in admins:
        return False
return True

def serve_get(client_socket, client_addr, details):
    try:
        #print details["client_data"], details["do_cache"], details["cache_path"], details["last_mtime"]
        client_data = details["client_data"]
        do_cache = details["do_cache"]
        cache_path = details["cache_path"]
        last_mtime = details["last_mtime"]

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((details["server_url"], details["server_port"]))
        server_socket.send(details["client_data"])

        reply = server_socket.recv(BUFFER_SIZE)
        if last_mtime and "304 Not Modified" in reply:
            print "returning cached file %s to %s" % (cache_path, str(client_addr))
            get_access(details["total_url"])
            f = open(cache_path, 'rb')
            chunk = f.read(BUFFER_SIZE)
            while chunk:
                client_socket.send(chunk)
                chunk = f.read(BUFFER_SIZE)
            f.close()
            leave_access(details["total_url"])

        else:
            if do_cache:
                print "caching file while serving %s to %s" % (cache_path, str(client_addr))
                get_space_for_cache(details["total_url"])
                get_access(details["total_url"])
                f = open(cache_path, "w+")
                # print len(reply), reply
                while len(reply):
                    client_socket.send(reply)
                    f.write(reply)
                    reply = server_socket.recv(BUFFER_SIZE)
                    #print len(reply), reply
                f.close()
                leave_access(details["total_url"])
                client_socket.send("\r\n\r\n")
            else:
                print "without caching serving %s to %s" % (cache_path, str(client_addr))
                #print len(reply), reply
                while len(reply):
                    client_socket.send(reply)
                    reply = server_socket.recv(BUFFER_SIZE)
                    #print len(reply), reply
                client_socket.send("\r\n\r\n")

        server_socket.close()
        client_socket.close()
        return

    except Exception as e:
        server_socket.close()
        client_socket.close()
        print e
        return




def Request_handler(Sock_client,Addr_client,Data_client):
	details = parse_details(client_addr, client_data)

    if not details:
        print "no any details"
        client_socket.close()
        return

    isb = is_blocked(client_socket, client_addr, details)

    """
        Here we can check whether request is from outside the campus area or not.
        We have IP and port to which the request is being made.
        We can send error message if required.
    """

    if isb:
        print "Block status : ", isb

    if isb:
        client_socket.send("HTTP/1.0 200 OK\r\n")
        client_socket.send("Content-Length: 11\r\n")
        client_socket.send("\r\n")
        client_socket.send("Error\r\n")
        client_socket.send("\r\n\r\n")

    elif details["method"] == "GET":
        details = get_cache_details(client_addr, details)
        if details["last_mtime"]:
            details = insert_if_modified(details)
        serve_get(client_socket, client_addr, details)

    elif details["method"] == "POST":
        serve_post(client_socket, client_addr, details)

    client_socket.close()
    print client_addr, "closed"
    print



def init_server():
    
    Sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    Sock_server.bind(('', 7777))
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


init_server()