import pickle
import socket
from object_class import Person, Car

def print_object(obj):
    if isinstance(obj, Car):
        print("Brand: " + obj.brand)
        print("Series: " + obj.series)
    elif isinstance(obj, Person):
        print("Name: " + obj.name)
        print("Age: " + str(obj.age))
    else:
        print("Unknown Object")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 7777))
server_socket.listen(5)

client_socket, client_address = server_socket.accept()

data = client_socket.recv(65535)
obj = pickle.loads(data)
print_object(obj)

data = client_socket.recv(65535)
obj = pickle.loads(data)
print_object(obj)


client_socket.close()
server_socket.close()