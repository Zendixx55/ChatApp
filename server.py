import socket  #handliog client connections
import threading  #creating a thread for each connection in order to run multiple connections simultaneously

import thread
global client_socket
global client_address
global clientlist
global ID
global username



def messagehandler(client_socket, username): #handling messages: accepting and sending to other users
    print(f"Started message handler for {username}")
    client_message = ''
    while client_message != 'quit':
        try:
            client_message = client_socket.recv(1024).decode()
            print(f"Received from {username}: {client_message}")
            t3 = threading.Thread(target=broadcast, args=(username, client_message))
            t3.start()
        except ConnectionResetError:
            print("Client " + username + " disconnected")
            client_socket.close()
            break
        except Exception as e:
            print("An error has occurred. \n" + str(e))
            break

def broadcast(nickname, client_message): # a broadcast function that sends the message to all connected clients
    broadcast_list = []
    for client in clientlist:
        try:
            client['client_socket'].send((f"{nickname}: {client_message}").encode())
            broadcast_list.append(client['client_socket'])
        except:
            pass
    print("Broadcast: " + str(broadcast_list))


def on_connect(client_socket, client_address, clientlist): #This function is used to retrieve user login information
    print("Client connected")
    client_socket.send("Welcome to ChatApp! Would you like to login or signup? ".encode())
    choice = ask_check_choice().strip()
    client_details = retrieve_username_and_password(client_socket, client_address, ID)
    if choice == 'login':
        if on_login(client_details ,clientlist):
            client_socket.send(f"Welcome back {client_details['username']}! Please write your message: ".encode())
        else:
            client_socket.send("You have tried logging in too many times, Please try reconnecting. \n".encode())
            client_socket.send("Quitting program.".encode())
            client_socket.close()
    elif choice == 'signup':
        on_signup(client_details, ID, clientlist)
        client_socket.send(f"Welcome {client_details['username']}, Please write your message: ".encode())
        # add_to_socketlist()
    else:
        client_socket.send("Please type login/ signup: ".encode())
        choice = client_socket.recv(1024).decode().lower().strip()
    t2 = threading.Thread(target=messagehandler, args=(client_socket, client_details['username']))
    t2.start()

def retrieve_username_and_password(client_socket , client_address, ID): # Asks client for username and password
    client_socket.send(("Please enter username: ").encode())
    username = client_socket.recv(1024).decode().strip()
    client_socket.send(("Please enter password: ").encode())
    password = client_socket.recv(1024).decode().strip()
    client_details = {  # creates a temporary dictionary with the clients details
        'client_address': client_address,
        'client_socket': client_socket,
        'username': username,
        'password': password,
        'ID': ID
    }
    return client_details

def on_login(client_details, clientlist): # Authenticate with existing client list
    attempts = 1
    while attempts < 3:
        for client in clientlist:
            print('client.get("username") is :' + client.get('username')) # debug
            print('client_details["username"] is: ' + client_details['username']) # debug
            if client.get('username') == client_details['username'] and client.get('password') == client_details['password']:
                client['client_socket'] = client_details['client_socket']
                client['client_address'] = client_details['client_address']
                return True
            else:
                pass
        client_socket.send(f"One of your credentials is wrong, please try again. {3 - attempts} attempts left ".encode())
        client_details = retrieve_username_and_password(client_details['client_socket'], client_details['client_address'])
        attempts += 1
    return False

def on_signup(client_details, ID, clientlist):
    clientlist.append({
                'client_socket': client_details['client_socket'],
                'client_address': client_details['client_address'],
                'username': client_details['username'],
                'password': client_details['password'],
                'ID': client_details['ID']
            })
    print("Client list updated: " + str(clientlist))
    ID += 1

def ask_check_choice():
    choice = client_socket.recv(1024).decode().lower().strip()
    while True:# check if choice for login/ signup is valid
        if choice == 'login' or choice == 'signup':
            print("choice: " + choice)
            return choice
        else:
            client_socket.send("Please type login/ signup: ".encode())
            choice = client_socket.recv(1024).decode().lower().strip()


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
        t1 = threading.Thread(target=on_connect, args=(client_socket, client_address, clientlist)) # starting client acception and message handling
        t1.start()

except Exception as e:
    print("Error!!!!")
    print(e)
    client_socket.close()
    server_socket.close()


# another option - dont allow 2 users have the same name
