#!/usr/bin/python
# Import socket module
import socket
 
 
def Main():
    # local host IP '127.0.0.1'
    host = '127.0.0.1'
    
    # Define the port on which you want to connect
    port = 1234
    
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # connect to server on local computer
    s.connect((host,port))
    
    #verify SSL
    data = s.recv(1024)
    ans = input(data)
    s.send(ans.encode('ascii'))
    if ans == 'Yes':
        data = s.recv(1024)
        print(data)
        data = s.recv(2048)
        print(data)
    
    #log in
    while True:
        
        data = s.recv(1024)
        if data == 'You are logged in\n':
            break
        ans = input(data)
        s.send(ans.encode('ascii'))
    
    # messages
    while True:
 
        message = input("Message to send")
        s.send(message.encode('ascii'))
        if message == 'END':
            break
        data = s.recv(1024)
        print('Received from the server :', str(data.decode('ascii')))

    s.close()
 
if __name__ == '__main__':
    Main()
