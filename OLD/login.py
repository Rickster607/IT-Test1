#!/usr/bin/python

import hashlib
import os

def main():
    register()

def register():
    print("REGISTER...")
    username = raw_input("Please input your desired username:")
    password = raw_input("Please input your desired password:")
    salt = os.urandom(16)
    m = hashlib.md5()
    m.update(salt + password)
    password=m.digest()
    file = open("accountfile.txt","a")
    file.write(username)
    file.write(" ")
    file.write(password)
    file.write("\n")
    file.close()
    if login():
        print("You are now logged in...")
    else:
        print("You aren't logged in!")

def login():
    print("LOGIN...")
    username = raw_input("Please enter your username:")
    password = raw_input("Please enter your password:")  
    for line in open("accountfile.txt","r").readlines(): # Read the lines
        login_info = line.split() # Split on the space, and store the results in a list of two strings
        if username == login_info[0] and password == login_info[1]:
            print("Correct credentials!")
            return True
    print("Incorrect credentials.")
    return False

# create a main function in Python
if __name__ == "__main__":
    main()
