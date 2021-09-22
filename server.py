#  coding: utf-8 
import socketserver
import sys
import mimetypes
from datetime import date
from os import path

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

dateFormat = "%a, %d %b %Y %H:%M:%S GMT"
VERBOSE = False

class Request():
    def __init__(self):
        self.protocol: str = "HTTP/1.1"
        self.method: str = "GET"
        self.resource: str = None
        self.headers: dict = {}

class Response():
    def __init__(self):
        self.protocol: str = "HTTP/1.1"
        self.headers: dict = {"Connection": "close"}
        self.data = None
        self.status: str= "200 OK"

    def compileResponse(self):
        strResponse = self.protocol + " " + self.status + "\r\n"
        if (not self.headers):
            self.headers = {}
        self.headers["Date"] = date.today().strftime(dateFormat)

        if self.data:
            self.headers["Content-Length"] = str(len(self.data))

        for name, value in self.headers.items():
            strResponse += name + ": " + value + "\r\n"
        
        strResponse += "\r\n" 

        if self.data:
            strResponse += self.data

        return strResponse

class MyWebServer(socketserver.BaseRequestHandler):
    root = path.dirname(path.abspath(__file__)) +  "/www"

    """
        parse the data into a Response object
    """
    def parseData(self):
        lines = self.data.decode("utf-8").split("\r\n")
        request = Request()
        isFirst = True
        for line in lines:
            split = None
            if isFirst:
                split = line.strip().split(" ")
                if (len(split) == 3):
                    request.resource = split[1]
                    request.protocol = split[2]
                    method = split[0].lower()
                    if (method == "get"):
                        request.method = "GET"
                    else:
                        request.method = split[0]
                else:
                    # TODO throw bad request error
                    print("request line has < or > 3 space seperated arguments")
                isFirst = False
            else:
                split = line.strip().split(":")

                if split:
                    # remove empty strings and extra whitespace
                    split[:] = [x.strip() for x in split if x.strip() != ""]
                
                if split and len(split) > 0:
                    val = None
                    if (len(split) > 1 ):
                        val = split[1]
                    request.headers[split[0]] = val
        return request

    """
        Gat a tuple where the first field is the absolute path to a file, or the path to the new location 
        to be returned with a 301 code, or None if the file doesn't exit. The second field is the status code
        to return for the file.
    """
    def getFilePath(self, originalPath: str):
        filePath = self.root + "/" + originalPath.lstrip("\\").lstrip("/")
        if (path.commonpath([self.root, path.abspath(filePath)]) == self.root):
            # Account for symbolic links as long as the link is located in the root.
            filePath = path.abspath(path.realpath(filePath))
            if (path.isdir(filePath)):
                if (originalPath.endswith("/")):
                    # default to index.html if the path is a directory with a valid ending
                    filePath += "/index.html"
                else:
                    # redirect if the path is a directory with an invalid ending
                    return (originalPath + "/", 301)

            if (path.exists(filePath)):
                return (filePath, 200)
        return (None, 404)

    """
        Get the encoding and content type for the file, 
        set the Content-Type header, and return the charset to use
        when opening the file
    """
    def getContentType(self, res: Response, filePath: str):
        contentType = mimetypes.guess_type(filePath, strict=True)
        encoding = "utf-8"
        if contentType and contentType[0]:
            if contentType[1]:
                encoding = contentType[1]
            res.headers["Content-Type"] = contentType[0] + "; charset=" + encoding
        else:
            res.headers["Content-Type"] = "text/plain; charset=" + encoding
        return encoding

    """
        Create a response including the requested resource if possible,
        or the proper error codes and messages if not possible
    """
    def handleGet(self, req: Request):
        res = Response()
        if (req.resource):
            filePath, statusCode = self.getFilePath(req.resource)
            if (filePath == None):
                res.status = "404 Not Found"
                res.data = "Could not find the requested resource"
            elif(statusCode == 200):
                file = open(filePath, "r", encoding=self.getContentType(res, filePath))
                res.data = file.read()
                res.headers["Last-Modified"] = date.fromtimestamp(path.getmtime(filePath)).strftime(dateFormat)
                res.status = "200 OK"
            elif(statusCode == 301):
                res.status = "301 Moved Permanently"
                res.data = "The requested file has permanently moved"
                res.headers["Location"] = filePath
        else:
            res.status = "400 Bad Request"
            res.data = "No Resource URI was included in the request"
        return res

    """
        Create a response with the 405 status code
    """
    def handleMethodNotAllowed(self):
        res = Response()
        res.status = "405 Method Not Allowed"
        res.headers["Allow"] = "GET"
        return res

    """
        Create a response with the 403 status code
    """
    def handleBadProtocol(self):
        res = Response()
        res.status = "403 Forbidden"
        res.data = "Unsupported Protocol"
        return res

    """
        Handle a given user request
    """
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s" % self.data)
        res: Response = None
        if (self.data):
            req = self.parseData()
            if (req.protocol != "HTTP/1.1"):
                res = self.handleBadProtocol()

            if (req.method == "GET"):
                res = self.handleGet(req)
            else:
                res = self.handleMethodNotAllowed()

        if (res):
            strResponse = res.compileResponse()
            self.request.sendall(bytearray(strResponse, "utf-8"))
            if VERBOSE:
                print(strResponse)
            else:
                print(res.status)
        print()

if __name__ == "__main__":
    if sys.argv and len(sys.argv) > 1: 
        if sys.argv[1] == "-v" or sys.argv[1] == "verbose":
            VERBOSE = True
        else:
            VERBOSE = False

    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
