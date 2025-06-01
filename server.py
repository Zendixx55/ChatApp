import socket  #handliog client connections
import threading  #creating a thread for each connection in order to run multiple connections simultaneously

import thread
global client_socket
global client_address
global clientlist
global ID
global username


def on_connect(client_socket, client_address, clientlist):  # This function is used to retrieve user login information
    print("[S] onconnect: Client connected")
    client_socket.send("Welcome to ChatApp! Would you like to login or signup? ".encode())
    choice = ask_check_choice().strip()
    client_details = retrieve_client_details(client_socket, client_address)
    ID = 0
    if choice == 'login':
        if on_login(client_details, clientlist):
            for client in clientlist:
                if client['username'] == client_details['username']:  # make sure
                    ID = client['ID']
                    client_socket.send(f"Welcome back {clientlist[ID]['username']}! Please write your message: ".encode())
                    break
        else:
            client_socket.send("You have tried logging in too many times, Please try reconnecting. \n".encode())
            client_socket.send("Quitting program.".encode())
            client_socket.close()
    elif choice == 'signup':
        on_signup(client_details, clientlist)
        ID = clientlist[-1]['ID']
        client_socket.send(f"Welcome {clientlist[-1]['username']}, Please write your message: ".encode())
    try:
        t2 = threading.Thread(target=messagehandler, args=(clientlist,ID))
        t2.start()
    except Exception as e:
        print(f'[Se] onconnect: An error has occurred.\n{e}')

def ask_check_choice():
    choice = client_socket.recv(1024).decode().lower().strip()
    while True:# check if choice for login/ signup is valid
        if choice == 'login' or choice == 'signup':
            return choice
        else:
            client_socket.send("Please type login/ signup: ".encode())
            choice = client_socket.recv(1024).decode().lower().strip()

def retrieve_client_details(client_socket, client_address): # Asks client for username and password
    client_socket.send(("Please enter username: ").encode())
    username = client_socket.recv(1024).decode().strip()
    client_socket.send(("Please enter password: ").encode())
    password = client_socket.recv(1024).decode().strip()
    client_details = {  # creates a temporary dictionary with the clients details
        'client_address': client_address,
        'client_socket': client_socket,
        'username': username,
        'password': password,
        'connected': False
    }
    return client_details

def on_login(client_details, clientlist): # Authenticate with existing client list
    attempts = 1
    while attempts < 3:
        for client in clientlist:
            if client.get('username') == client_details['username'] and client.get('password') == client_details['password']:
                client['client_socket'] = client_details['client_socket']
                client['client_address'] = client_details['client_address']
                client['connected'] = True
                broadcast(client['username'],client_message='connected')
                return True
            else:
                pass
        client_socket.send(f"One of your credentials is wrong, please try again. {3 - attempts} attempts left ".encode())
        client_details = retrieve_client_details(client_details['client_socket'], client_details['client_address'], ID)
        attempts += 1
    return False

def on_signup(client_details, clientlist):
    while True:
        ID = new_user_ID(clientlist)
        if any(client_details['username'] == client.get('username') for client in clientlist):
            client_socket.send(f"{client_details['username']} is not available, please try again.".encode())
        else:
            clientlist.append({
                    'client_socket': client_details['client_socket'],
                    'client_address': client_details['client_address'],
                    'username': client_details['username'],
                    'password': client_details['password'],
                    'ID': ID,
                    'connected' : True
                })
            broadcast(clientlist[ID]['username'], client_message='connected')
            print("[S] singup: Client list updated: " + str(clientlist))
            break
        client_details = retrieve_client_details(client_details['client_socket'], client_details['client_address'])

def messagehandler(clientlist, ID): # handling messages: accepting and sending to other users
    client = clientlist[ID]
    print(f"[S] MH: Started message handler for {client['username']}")
    client_message = client['client_socket'].recv(1024).decode()
    while client_message != 'quit' and client_message != 'exit':
        try:
            if not client_message:
                continue
            elif client_message == '!show connected':
                online = []
                for n in clientlist:
                    if n['connected']:
                        online.append(n['username'])
                client['client_socket'].send((f"Connected users: {online}").encode())
            else:
                print(f"[S] MH: Received from {client['username']}: {client_message}")
                broadcast(client['username'], client_message)
        except ConnectionResetError: # in case client disconnects without quit/ exit command
            client['connected'] = False
            print("[Se] MH: Client " + client['username'] + " disconnected")
            client['client_socket'].close()
            break
        except Exception as e:
            print(f"[Se] MH: An error has occurred. \n{e}")
            break
        client_message = client['client_socket'].recv(1024).decode()
    broadcast(client['username'], client_message)
    client['connected'] = False
    print("[S]MH: Client " + client['username'] + " disconnected")
    client['client_socket'].close()

def broadcast(username, client_message ): # a broadcast function that sends the message to all connected clients
    for client in clientlist:
        ID = client['ID']
        if client['connected']:
            try:
                if client_message == 'quit' or client_message == 'exit':
                    client['client_socket'].send((f"[!] User {username} Disconnected.").encode())
                elif client_message == 'connected':
                    client['client_socket'].send((f"[!] User {username} is connected.").encode())

                else:
                    client['client_socket'].send((f"{username}: {client_message}").encode()) # actual broadcast line
            except BrokenPipeError: # in case client disconnects without quit/ exit command
                client['connected'] = False
                for n in clientlist:
                    if n['connected']:
                        n['client_socket'].send((f"[!] User {client['username']} Disconnected.").encode())
                print("[S] BC: Client " + client['username'] + " disconnected")
                client['client_socket'].close()
                pass
            except Exception as e:
                print(f"[Se] BC: Error occurred while broadcasting. failed to send message to: {client['username']}\nError: {e}")
                pass

def new_user_ID(clientlist): # Will check for the last ID in client list and return a new ID for new user
    IDlist = []
    IDvalue = 0
    for client in clientlist:
        IDlist.append(client['ID'])
    if len(IDlist) == 0:
        return IDvalue
    for n in IDlist:
        if n >= IDvalue:
            IDvalue = n
    return IDvalue + 1

port = 1337 #defying port number for connections
clientlist = [] # empty client list to be filled later
ID = 0 # user connection ID

try:
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0' , port))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen() #this and all 4 lines before starting the server and listening for connections
    print(f"[S] Server is listening on port {port}")
    try:
        while True:
            client_socket, client_address = server_socket.accept() # looping server acceptations
            t1 = threading.Thread(target=on_connect, args=(client_socket, client_address, clientlist,)) # starting client acceptation and message handling
            t1.start()
    except Exception as e:
        print(f"[S] An error occurred while accepting client connection:\n{e}")
        server_socket.close()
except Exception as e2: # try except was made for production stage when server crashes and need to wait for address to be available again
    print(f"[S] An error has occurred while starting server:\n{e2}")



# add show connected option