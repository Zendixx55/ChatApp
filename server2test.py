import socket  #handliog client connections
import threading  #creating a thread for each connection in order to run multiple connections simultaneously

import thread
global client_socket
global client_address
global clientlist
global ID
global username

def newclient(): #creating a new client identification function
    global ID
    while True:
        (client_socket, client_address) = server_socket.accept()
        print("Client connected")
        print(type(client_socket))
        client_socket.send(("Hello, please enter username: ").encode())
        username = client_socket.recv(1024).decode().strip()
        clientlist.append({
            'client_socket':client_socket ,
            'client_address': client_address,
            'username':username,
            'ID': ID
        })
        client_socket.send(f"Welcome {str(clientlist[ID-1]['username'])}! Please write your message:".encode())

        while len(clientlist) == 0:
            pass

        t2 = threading.Thread(target=messagehandler,
                              args=(clientlist[ID - 1]['client_socket'], clientlist[ID - 1]['username']))
        t2.start()
        ID += 1

def messagehandler(client_socket, nickname): #handling messages: accepting and sending to other users
    print(f"Started message handler for {nickname}")
    client_message = client_socket.recv(1024).decode()
    while client_message != 'quit':
        # client_socket.send((f"{nickname}: {client_message}").encode())
        client_message = client_socket.recv(1024).decode()
        print(f"Received from {nickname}: {client_message}")
        t3 = threading.Thread(target=add_to_list)
        t3.start()
        t4 = threading.Thread(target=broadcast, args=(nickname,client_message))
        t4.start()

    client_socket.close()

def add_to_list(): #in order to send every client the messages incoming - we need to have a list of all connected clients
    for socket in clientlist:
        socket = socket['client_socket']
        if socket not in socketlist:
            socketlist.append(socket)
            print(socketlist)


def broadcast(nickname, client_message): # a broadcast function that sends the message to all connected clients
    print("Broadcasting to: ", socketlist)
    for socket in socketlist:
        socket.send((f"{nickname}: {client_message}").encode())


port = 1337 #defying port number for connections
clientlist = [] # empty client list to be filled later
socketlist = [] # empty socket list to be filled later
ID = 1 # user connection ID
try:
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0' , port))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen() #this and all 4 lines before starting the server and listening for connections
    print(f"Server is listening on port {port}")
except Exception as e2: # try except was made for production stage when server crashes and need to wait for address to be available again
    print("Error!!!!")
    print(e2)
    client_socket.close()
    server_socket.close()

try:
    t1 = threading.Thread(target=newclient)
    t1.start()
except Exception as e:
    print("Error!!!!")
    print(e)
    client_socket.close()
    server_socket.close()


# option- add a quit function to delete the user from the client list
# another option - dont allow 2 users have the same name
