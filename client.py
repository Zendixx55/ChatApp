import socket
import threading

def listen_to_messages():
    while True:
        messages = client_socket.recv(1024).decode()
        print(messages)

def send_message():
    while True:
        command = input('> ')
        client_socket.send(command.encode())

client_socket = socket.socket()
client_socket.connect(('127.0.0.1' , 1337)) # Change to the servers IP address

listening_thread = threading.Thread(target=listen_to_messages)
sending_thread = threading.Thread(target=send_message)

listening_thread.start()
sending_thread.start()


