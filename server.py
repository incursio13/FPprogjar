#!/usr/bin/env python
#http://ilab.cs.byu.edu/python/threadingmodule.html 
import select
import socket
import sys
import threading
import os
import re

class Server:
    def __init__(self):
        self.host = ''
        f=open('httpserver.conf','r')
        data=f.read();
        data=data.split(':')[1]
        f.close()
        self.port = int(data)
        self.backlog = 5
        self.size = 4096
        self.server = None
        self.threads = []

    def open_socket(self):        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host,self.port))
        self.server.listen(5)
        
    def run(self):
        self.open_socket()
        input = [self.server, sys.stdin]
        running = 1
        while running:
            inputready,outputready,exceptready = select.select(input,[],[])

            for s in inputready:

                if s == self.server:
                    # handle the server socket
                    c = Client(self.server.accept())
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = 0

        # close all threads
        self.server.close()
        for c in self.threads:
            c.join()

class Client(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 4096

    def run(self):
        running = 1
        while running:
            response_header=''
            data = self.client.recv(4096)                                                                
            if data:
                print data                                  
                
                request_header = data.split('\r\n')
                request_file = request_header[0].split(' ',1)[1].split('HTTP')[0].strip()
                
                if '%20' in request_file:
                    i=0
                    temp=re.split(r'%20',request_file)
                    request_file=''
                    print temp
                    while i<len(temp):
                        request_file=request_file+temp[i]
                        if i<len(temp):
                            request_file+=' '
                            i+=1
                    request_file=request_file.strip()
                                    
                for dirname, dirnames, filenames in os.walk('.'):
                    for subdirname in dirnames:
                        if os.path.join(dirname,subdirname)[1:]==request_file or os.path.join(dirname,subdirname)[1:]==request_file[:-1]:
#                            print os.path.join(dirname,subdirname)[1:];
#                            print dirname+subdirname;
                            if os.path.exists(request_file[1:]+'/index.html'):
                                filename=request_file[1:]+'/index.html'
                                f = open(filename,'r')
                                response_data = f.read()
                                f.close()
                                content_length = len(response_data)
                                response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' + str(content_length) + '\r\n\r\n'                    
                            else:
                                dirs = os.listdir(request_file[1:])
                                list_dir='<html><body><h1>Direktory</h1>\r\n'
                                for file in dirs:
                                    if os.path.isdir(request_file[1:]+"/"+file):
                                        list_dir=list_dir+'<a href="/dataset/'+file+'">'+file+'</a></br>\r\n'
                                    else:
                                        list_dir=list_dir+'<a href="/dataset/'+file+'" download="/dataset/'+file+'">'+file+'</a></br>\r\n'
                                response_data = list_dir+"</body></html>"        
                                content_length = len(list_dir)
                                response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' + str(content_length) + '\r\n\r\n'                    
                                break
#                        print(os.path.join(dirname, subdirname))
                    for filename in filenames:  
                        if os.path.join(dirname,filename)[1:]==request_file:
                            nama_filenya=request_file.split('/')[2]
                            temp=request_file[1:]
                            f = open(temp,'rb')
                            response_data = f.read()
                            f.close()
                            content_length = len(response_data)
                            response_header = 'HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream; charset=UTF-8\r\nContent-Disposition: attachment; filename:'+nama_filenya+'\r\nContent-Length:' + str(content_length) + '\r\n\r\n'                    
                            break
                        
#                    if '.git' in dirnames:
#                        dirnames.remove('.git')                
                
                if request_file == '/index.html' or request_file == '/' :                
                    f = open('index.html','r')
                    response_data = f.read()
                    f.close()
                    
                    content_length = len(response_data)
                    response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' + str(content_length) + '\r\n\r\n'                    
                elif response_header=='':
                    f = open('404.html','r')
                    response_data = f.read()
                    f.close()
                    content_length = len(response_data)
                    response_header = 'HTTP/1.1 404 NOT FOUND\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' + str(content_length) + '\r\n\r\n'                    
                
                print response_header                
                self.client.sendall(response_header + response_data)  

            else:
                self.client.close()
                running = 0
#            except KeyboardInterrupt:        
#                self.client.close()
#                running = 0
                
if __name__ == "__main__":
    s = Server()
    s.run() 