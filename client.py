import socket
import sys
from bs4 import BeautifulSoup

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.181.1.242', 50002)
client_socket.connect(server_address)

request_header = 'GET '
request_header2= ' HTTP/1.0\r\nHost: 10.181.1.242\r\n\r\n'
#client_socket.send(request_header)

try:
    
    while True:
        response = ''
        isi_file = ''
        command=raw_input('request : ')
        request_header_fix=request_header+command+request_header2
        
        client_socket.send(request_header_fix)
        
        recv = client_socket.recv(1024)
       # print recv
        panjang_isi=int(recv.split('Content-Length:')[1].split('\r\n\r\n')[0])
        
        is_download=recv.split('Content-Type:')[1].split(';')[0].strip()
        if is_download=='application/octet-stream':
            nama_file=recv.split('filename:')[1].split('\r')[0]
         #   print nama_file
            
        isi_file=recv.split('\r\n\r\n',1)[1]
#        print isi_file
        panjang_data=len(isi_file)
        response += recv

        while panjang_data < panjang_isi :
            
            recv = client_socket.recv(1024)
            panjang_data+= len(recv)
            response += recv
            isi_file += recv
            
        if is_download=='application/octet-stream':
            f=open(nama_file,'wb')
            f.write(isi_file)
            f.close()
        else:
            soup = BeautifulSoup(response)
            print soup.get_text()
#            print response
        #/dataset/contoh.html
        if not recv:
            break
        #
        

    client_socket.close()    

except KeyboardInterrupt:
	client_socket.close()
	sys.exit(0)