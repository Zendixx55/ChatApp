import socket
import time



client_socket = socket.socket()
client_socket.connect(('127.0.0.1' , 1337)) # Change to the servers IP address

while True:
    messages = client_socket.recv(1024).decode()
    print(messages)
    command = input('Your message: ')
    client_socket.send(command.encode())


