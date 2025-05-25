import socket
import threading
import time


# def listen_for_messages():
#     messages = client_socket.recv(1024).decode()
#     print(messages)

client_socket = socket.socket()
client_socket.connect(('127.0.0.1' , 1337))
# command = input('Terminal: ')
# t1 = threading.Thread(target=listen_for_messages)
# t1.start()
while True:
    messages = client_socket.recv(1024).decode()
    print(messages)
    command = input('Your message: ')
    client_socket.send(command.encode())


