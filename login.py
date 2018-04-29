#!/usr/bin/python

import hashlib
import os

def main():
	answer = raw_input("Have you logged into this server before?  Yes/No\n")
	a = answer.lower()
	if(a== "yes"):
		login()
	else:
		register()

def register():
	username = raw_input("Please input your desired username:\n")
	password = raw_input("Please input your desired password:\n")
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
	username = raw_input("Please enter your username:\n")
	password = raw_input("Please enter your password:\n")
	n = hashlib.md5()
	n.update(password)
	password = n.digest()
	didFind=0
	for line in open("accountfile.txt", "r").readlines():
		login_info = line.split()
		if username == login_info[0] and password == login_info[1]:
			print("You are logged in!")
			didFind=1
			return
		else:
			continue
	count = 0
	while count < 3 and didFind == 0:
		print("Wrong username or password, please try again:\n")
		username = raw_input("Please enter your username:\n")
		password = raw_input("Please enter your password:\n")
		k = hashlib.md5()
		k.update(password)
		password = k.digest()
		file = open("accountfile.txt", "r")
		for line in file.readlines():
			login_info = line.split()
			if username == login_info[0] and password == login_info[1]:
				print("You are logged in!")
				didFind = 1
				return
			else:
				continue
		count += 1
		file.close()
	print("You have used all your login attempts")
if __name__ == "__main__":
    main()
