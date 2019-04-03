import sys
import os
import time
import socketserver
import http.server

if len(sys.argv) < 2:
    print("Needs one argument: server port")
    raise(SystemExit)

PORT = int(sys.argv[1])

class HTTPCacheRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        if self.command != "POST" and self.headers.get('If-Modified-Since', None):
            name_file = self.path.strip("/")
            if os.path.isfile(name_file):
                a = time.strptime(time.ctime(os.path.getmtime(name_file)), "%a %b %d %H:%M:%S %Y")
                b = time.strptime(self.headers.get('If-Modified-Since', None), "%a %b %d %H:%M:%S %Y")
                if a < b:
                    self.send_response(304)
                    self.end_headers()
                    return None
        return http.server.SimpleHTTPRequestHandler.send_head(self)

    def end_headers(self):
        self.send_header('Cache-control', 'must-revalidate')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

    def do_POST(self):
        self.send_response(200)
        self.send_header('Cache-control', 'no-cache')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

temp = socketserver.ThreadingTCPServer(("", PORT), HTTPCacheRequestHandler)
temp.allow_reuse_address = True
print("Serving on port", PORT)
temp.serve_forever()