#!/usr/bin/python

import hashlib
import os
import socket
from _thread import*
import threading

print_lock = threading.Lock()

def threaded(c):
	message = "Would you like to verify this server's SSL certificate? Yes/No"
	c.send(message)
	answer = c.recv(100)
	a = answer.lower()
	if(a == "yes"):
		f = open('domain.crt', 'rb')
		l = f.read(2048)
		data = "Sending domain.crt...\n"
		c.send(data)
		c.send(l)
	data = "Have you logged into this server before? Yes/No\n"
	c.send(data)
	answer = c.recv(40)
	a = answer.lower()
	if(a=="yes"):
		n = login()
	else:
		register()
	if(n==1)
		message = "The groups are..."
		c.send(data)
		while true:
			data = s.recv(1024)
			if(data == "END"):
				#
			if(data == "GET"):
			   	#
			if(data == "POST"):
				#
			print_lock.release()
		c.close()


def main():
	host = ""
	port = 12345
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	s.bind((host, port))
	print("Socket bound to port", port)

	s.listen(5)

	while True:
		c, addr = s.accept()
		print_lock.acquire()
		start_new_thread(threaded, (c,))

	s.close()

def register():
	data = "Please input your desired username:"
	c.send(data)
	username = c.recv(100)
	data = "Please input your desired password:"
	c.send(data)
	password = c.recv(100)
	m = hashlib.md5()
	m.update(password)
	password = m.digest()
	file = open("accountfile.txt", "a")
	file.write(username)
	file.write(" ")
	file.write(password)
	file.write("\n")
	file.close()
	print("You are now registered and logged in\n")
	return

def login():
	data = "Please input your desired username:"
	c.send(data)
	username = c.recv(100)
	data = "Please input your desired password:"
	c.send(data)
	password = c.recv(100)
	n = hashlib.md5()
	n.update(password)
	password = n.digest()
	didFind=0
	for line in open("accountfile.txt", "r").readlines():
		login_info = line.split()
		if username == login_info[0] and password == login_info[1]:
			print("You are logged in!")
			didFind=1
			return 1
		else:
			continue
	count = 0
	while count < 3 and didFind == 0:
		data = "Wrong username or password, please try again"
		c.send(data)
		data = "Please enter your username:"
		c.send(data)
		username = c.recv(100)
		data = "Please enter your password"
		c.send(data)
		password = c.recv(100)
		k = hashlib.md5()
		k.update(password)
		password = k.digest()
		file = open("accountfile.txt", "r")
		for line in file.readlines():
			login_info = line.split()
			if username == login_info[0] and password == login_info[1]:
				data = "You are logged in"
				c.send(data)
				didFind = 1
				return 1
			else:
				continue
		count += 1
		file.close()
	data = "You have used all your login attempts"
	c.send(data)
if __name__ == "__main__":
    main()
