import pickle
import socket
from object_class import Car, Person

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 7777))



# mylist = []
# mylist.append("this is a string")
# mylist.append(5)
# mylist.append(('localhost', 5000))

# print(mylist)

person = Person("Bryan", 11)
print(person)

car = Car("Hyundai", "120")
print(car)

p_list = pickle.dumps(person)
print(p_list)
client_socket.send(p_list)

p_list = pickle.dumps(car)
print(p_list)
client_socket.send(p_list)

client_socket.close()