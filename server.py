#  coding: utf-8 
import socketserver
import os.path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        # Get the request data
        self.data = self.request.recv(1024).strip()
        dataString = self.data.decode('utf-8')

        # Check the request method
        if ("GET" not in dataString):
            self.__send_status("405 Method Not Allowed")
            return
        
        # Check the path
        path = self.__get_path(dataString)
        base_dir = os.path.dirname("www/")

        # Route the request
        self.__handle_get(base_dir + path)

    # Handles GET requests
    def __handle_get(self, path):
        if not os.path.exists(path):
            if not os.path.exists(path + '/'):
                self.__send_status("404 Not Found")
                return
            else:
                path = path + '/'
        (dirname, filename) = os.path.split(path)
        if (path.endswith("/")):
            self.__send_status("200 OK")
            self.__send_html_content(os.path.join(path, "index.html"))
        elif (os.path.splitext(filename)[1] == ".html"):
            self.__send_status("200 OK")
            self.__send_html_content(path)
        elif (os.path.splitext(filename)[1] == ".css"):
            self.__send_status("200 OK")
            self.__send_css_content(path)
        else:
            self.__send_status("301 Moved Permanently")
            path = path.replace("www/", "")
            self.request.sendall(bytearray('Location: http://' + HOST + ":" + str(PORT) + "/" + path + '/\r\n\r\n', 'utf-8'))

    # Returns 1 if the path is valid, 0 otherwise
    def __check_path(self, dirname, filename):
        try:
            open(os.path.join("www", dirname, filename))
            return 1
        except:
            try:
                open(os.path.join("www", dirname, "index.html"))
            except:
                return 0

    # Sends html content at the specified path
    def __send_html_content(self, path):
        page = open(path, 'r')
        self.request.sendall(bytearray('Content-Type: text/html\r\n\r\n', 'utf-8'))
        self.request.sendall(bytearray(page.read(),'utf-8'))

    # Sends css content at the specified path
    def __send_css_content(self, path):
        page = open(path, 'r')
        self.request.sendall(bytearray('Content-Type: text/css\r\n\r\n', 'utf-8'))
        self.request.sendall(bytearray(page.read(),'utf-8'))

    # Send the status code
    def __send_status(self, statusCode):
        self.request.sendall(bytearray('HTTP/1.1 ' + statusCode + '\r\n', 'utf-8'))

    # Gets the path given a string of the received data
    def __get_path(self, dataString):
        startIndex = dataString.index(" ") + 1
        endIndex = dataString.index("HTTP/1.1") - 1
        return dataString[startIndex:endIndex]

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
