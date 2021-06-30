import pickle

mylist = []
mylist.append("this is a string")
mylist.append(5)
mylist.append(('localhost', 5000))

print(mylist)

p_list = pickle.dumps(mylist)

print(p_list)