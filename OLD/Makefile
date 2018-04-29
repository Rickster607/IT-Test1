
all: server client

server: server.c
	gcc -g -pthread -lnsl server.c -o server

client: client.c
	gcc -g -lnsl client.c -o client

clean:
	rm -f client server
