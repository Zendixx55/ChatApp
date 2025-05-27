import socket  #handliog client connections
import threading  #creating a thread for each connection in order to run multiple connections simultaneously

import thread
global client_socket
global client_address
global clientlist
global ID
global username

# def newclient(): #creating a new client identification function
#     global ID
#     while True:
#         (client_socket, client_address) = server_socket.accept()
#         print("Client connected")
#         print(type(client_socket))
#         client_socket.send(("Hello, please enter username: ").encode())
#         username = client_socket.recv(1024).decode().strip()
#         clientlist.append({
#             'client_socket':client_socket ,
#             'client_address': client_address,
#             'username':username,
#             'ID': ID
#         })
#         client_socket.send(f"Welcome {str(clientlist[ID-1]['username'])}! Please write your message:".encode())
#
#         while len(clientlist) == 0:
#             pass
#
#         t2 = threading.Thread(target=messagehandler,
#                               args=(clientlist[ID - 1]['client_socket'], clientlist[ID - 1]['username']))
#         t2.start()
#         ID += 1

def messagehandler(client_socket, nickname): #handling messages: accepting and sending to other users
    print(f"Started message handler for {nickname}")
    client_message = ''
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

def on_connect(client_socket, client_address): #This function is used to retreive user login information
    print("Client connected")
    client_socket.send("Welcome to ChatApp! Would you like to login or signup? ".encode())
    choice = client_socket.recv(1024).decode().lower().strip()
    print("login/ signup : " +choice)
    while True:
        if choice == 'login' or choice == 'signup':
            break
        else:
            client_socket.send("Please type login/ signup: ".encode())
            choice = client_socket.recv(1024).decode().lower()
    username, password = retrieve_username_and_password(client_socket) # retrieves username and password
    client_details = { #creates a temporary dictionary with the clients details
        'client_address': client_address,
        'client_socket': client_socket,
        'username': username,
        'password': password
    }
    print("Temp client details received: " + str(client_details))
    if choice == 'login':
        on_login(client_details ,clientlist)
        client_socket.send(f"Welcome back {username}! Please write your message: ".encode())
        add_to_list()
    elif choice == 'signup':
        on_signup(client_details, ID)
        client_socket.send(f"Welcome {username}, Please write your message: ".encode())
        add_to_list()
    t2 = threading.Thread(target=messagehandler, args=(client_socket, username))
    t2.start()



def retrieve_username_and_password(client_socket): # Asks client for username and password
    client_socket.send(("Please enter username: ").encode())
    username = client_socket.recv(1024).decode().strip()
    client_socket.send(("Please enter password: ").encode())
    password = client_socket.recv(1024).decode().strip()
    return username, password

def on_login(client_details, clientlist ): # Authenticate with existing client list
    for client in clientlist:
        attempts = 1
        while attempts < 3:
            if client.get('username') == client_details['username'] and client.get('password') == client_details['password']:
                client['client_socket'] = client_details['client_socket']
                client['client_address'] = client_details['client_address']
                break
            else:
                client_socket.send(f"One of your credentials is wrong, please try again. {3 - attempts} attempts left ".encode())
                attempts += 1

def on_signup(client_details, ID):
    clientlist.append({
                'client_socket': client_details['client_socket'],
                'client_address': client_details['client_address'],
                'username': client_details['username'],
                'password': client_details['password'],
                'ID': ID
            })
    ID += 1
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
    server_socket.close()

try:
    while True:
        client_socket, client_address = server_socket.accept() # looping server acceptions
        t1 = threading.Thread(target=on_connect, args=(client_socket, client_address)) # starting client acception and message handling
        t1.start()

except Exception as e:
    print("Error!!!!")
    print(e)
    client_socket.close()
    server_socket.close()


# option- add a quit function to delete the user from the client list
# another option - dont allow 2 users have the same name
