import socket 
import threading
import _thread as thread

def Request_handler(Sock_client,Addr_client,Data_client):
    Sock_client.send(b'hey sexy')
    Sock_client.close()


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

            # print(Data_client.splitline())
            thread.start_new_thread(Request_handler,(Sock_client,Addr_client,Data_client))

        except KeyboardInterrupt:
            Sock_client.close()
            Sock_server.close()
            break


init_server()