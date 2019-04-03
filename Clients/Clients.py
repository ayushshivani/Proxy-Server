import os
import sys
import random
import time

if len(sys.argv) < 4:
    print("ERROR ::: Usage: python3 client.py <CLIENT_PORT> <PROXY_PORT> <REQUESTED_SERVER_PORT>")
    exit() 

CLIENT_PORT = sys.argv[1]	
PROXY_PORT  = sys.argv[2]
SERVER_PORT = sys.argv[3]

while True:
    file = "testfile.txt"
    METHOD = "POST"
    curl_string = "curl --request " + METHOD + " --proxy 127.0.0.1:" + PROXY_PORT +" --local-port  " + CLIENT_PORT + " 127.0.0.1:" + SERVER_PORT + "/" + file
    os.system(curl_string)
    time.sleep(10)