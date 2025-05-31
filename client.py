import socket
import threading

running = True  # Shared flag between threads

def listen_to_messages():
    global running
    while running:
        try:
            messages = client_socket.recv(1024).decode()
            if not messages:
                break
            if messages == "Quitting program.":
                print("Connection Lost.")
                running = False
                break
            print(messages)
        except:
            break

    client_socket.close()

def send_message():
    global running
    while running:
        try:
            command = input('> ')
            if command.lower() in ["quit", "exit"]:
                running = False
                client_socket.send(command.encode())
                break
            client_socket.send(command.encode())
        except:
            client_socket.close()
            break

    client_socket.close()

client_socket = socket.socket()
client_socket.connect(('127.0.0.1' , 1337)) # Change to the servers IP address

listening_thread = threading.Thread(target=listen_to_messages)
sending_thread = threading.Thread(target=send_message)

listening_thread.start()
sending_thread.start()


