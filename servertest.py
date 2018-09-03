import sys
import time
import http.server
from ctypes import *

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            print("IN GET" + str(self.path))
            data = create_string_buffer(str.encode("<HTML>there's life jim ---</HTML>" + str(self.date_time_string())))
            self.send_response(200)
            self.do_HEAD()
            self.wfile.write(data)
        except Exception as e:
            print(e)

    def do_HEAD(self):
        print("headers")
        self.send_header("Content-type:","text/plain")
        self.send_header('Date', self.date_time_string())
        self.end_headers()

    def do_POST(self):
        print("in POST")

    def log_request(self, code=None, size=None):
        print("in log_request")
        return

    def log_message(self, format, *args):
        print("in log_message")
        print("format = " + str(format))
        print("args = " + str(args))
        return

    def date_time_string(self):
        now = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.localtime(now)
        #there was a space between first , and %02d
        s = "%s,%02d %3s %4d %02d:%02d:%02d GMT" % (
        self.weekdayname[wd],
        day, self.monthname[month], year,hh, mm, ss)
        return s

class test_server():
    server_class = http.server.HTTPServer
    httpd = server_class(("",82), MyHandler)
    try:
        httpd.serve_forever()
    except Exception as e:
        print(e)
        httpd.server_close()
        sys.exit()

if __name__ == '__main__':
    tx = test_server