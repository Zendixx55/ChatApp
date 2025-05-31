import socket  #handliog client connections
import threading  #creating a thread for each connection in order to run multiple connections simultaneously

import thread
global client_socket
global client_address
global clientlist
global ID
global username


def on_connect(client_socket, client_address, clientlist):  # This function is used to retrieve user login information
    print("[S] Client connected")
    client_socket.send("Welcome to ChatApp! Would you like to login or signup? ".encode())
    choice = ask_check_choice().strip()
    client_details = retrieve_client_details(client_socket, client_address)
    ID = 0
    if choice == 'login':
        if on_login(client_details, clientlist):
            for client in clientlist:
                if client['username'] == client_details['username']:  # make sure
                    ID = client['ID']
                    print(ID)
                    client_socket.send(f"Welcome back {clientlist[ID - 1]['username']}! Please write your message: ".encode())
                    break
            print('ID after signup: ' + str(ID)) # debug
            # connected = True
            # broadcast()
        else:
            client_socket.send("You have tried logging in too many times, Please try reconnecting. \n".encode())
            client_socket.send("Quitting program.".encode())
            client_socket.close()
    elif choice == 'signup':
        on_signup(client_details, clientlist)
        print(str(clientlist))  # debug
        client_socket.send(f"Welcome {clientlist[-1]['username']}, Please write your message: ".encode())
    print("ID before t2: " + str(ID)) # debug
    t2 = threading.Thread(target=messagehandler, args=(client_socket, clientlist[ID - 1]['username']))
    t2.start()

def ask_check_choice():
    choice = client_socket.recv(1024).decode().lower().strip()
    while True:# check if choice for login/ signup is valid
        if choice == 'login' or choice == 'signup':
            print("choice: " + choice)
            return choice
        else:
            client_socket.send("Please type login/ signup: ".encode())
            choice = client_socket.recv(1024).decode().lower().strip()

def retrieve_client_details(client_socket, client_address): # Asks client for username and password
    client_socket.send(("Please enter username: ").encode())
    username = client_socket.recv(1024).decode().strip()
    client_socket.send(("Please enter password: ").encode())
    password = client_socket.recv(1024).decode().strip()
    print("ID for retrieve: " + str(ID)) # debug
    client_details = {  # creates a temporary dictionary with the clients details
        'client_address': client_address,
        'client_socket': client_socket,
        'username': username,
        'password': password,
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
            print("after append" + str(ID)) # debug
            print("[S] Client list updated: " + str(clientlist))
            break
        client_details = retrieve_client_details(client_details['client_socket'], client_details['client_address'])

def messagehandler(client_socket, username): #handling messages: accepting and sending to other users
    print(f"[S] Started message handler for {username}")
    client_message = ''
    while client_message != 'quit':
        try:
            client_message = client_socket.recv(1024).decode()
            if not client_message:
                continue
            else:
                print(f"[S] Received from {username}: {client_message}")
                t3 = threading.Thread(target=broadcast, args=(username, client_message))
                t3.start()
        except ConnectionResetError:
            print("[S] Client " + username + " disconnected")
            client_socket.close()
            break
        except Exception as e:
            print("[Se] An error has occurred. \n" + str(e))
            break

def broadcast(username, client_message ): # a broadcast function that sends the message to all connected clients
    broadcast_list = []
    for client in clientlist:
        try:
            # if connected:
            #     client['client_socket'].send((f"[*] {username} Connected.").encode())
            #     broadcast_list.append(client['client_socket'])
            # elif disconnected:
            #     client['client_socket'].send((f"[*] {username} disconnected").encode())
            #     broadcast_list.append(client['client_socket'])
            # else:
                client['client_socket'].send((f"{username}: {client_message}").encode())
                broadcast_list.append(client['client_socket'])
        except Exception as e:
            print(f"[Se] Error occurred while broadcasting. failed to send message to: {client['username']}\nError: {e}")
            pass
    print("[S] Broadcast: " + str(broadcast_list))

def new_user_ID(clientlist): # Will check for the last ID in client list and return a new ID for new user
    assignedID = 1
    for client in clientlist:
        IDvalue = client['ID']
        try:
            if assignedID < IDvalue:
                pass
            elif assignedID == IDvalue:
                assignedID = IDvalue + 1
                break
        except Exception as e:
            print("[Se] Error occurred while checking last ID: " + str(e))
    return assignedID




port = 1337 #defying port number for connections
clientlist = [] # empty client list to be filled later
socketlist = [] # empty socket list to be filled later
ID = 0 # user connection ID
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
        client_socket, client_address = server_socket.accept() # looping server acceptations
        t1 = threading.Thread(target=on_connect, args=(client_socket, client_address, clientlist)) # starting client acceptation and message handling
        t1.start()


except Exception as e:
    print("Error!!!!") # rephrase
    print(e)
    client_socket.close()
    server_socket.close()

# add user connected/ disconnected broadcast message
# add show connected option