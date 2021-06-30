import socket, threading
from Command_wrapper import Command_Wrapper

def read_msg(clients, client_socket, client_address, client_username):
    while True:
        try:
            data = client_socket.recv(65535)
        except:
            del clients[client_username]
            break
        #if len(data) == 0:
            #client_socket.close()
        #    break
        
        try:
            command, dest, args = data.decode("utf-8").split("||", 2)
        except:
            continue

        if not check_client_exist(command, dest, client_socket):
            continue

        executeable_func[command](client_username, client_socket, dest, args)
    
    client_socket.close()
    print("Connection closed", client_address)

def check_client_exist(command, dest, client_socket):
    # print(clients.keys())
    if command == "friendList" or command == "bcast":
        return True

    if dest in clients.keys():
        return True
    else:
        client_socket.send(bytes(f"notExist||{dest}", "utf-8"))
        return False

def check_if_in_friend_list(client_username, client_socket, dest):
    if dest not in client_friend[client_username]:
        client_socket.send(bytes(f"notFriend||{dest}", "utf-8"))
        return False
    return True

# def send_broadcast(clients, data, client_socket, client_username):
#     for dest_client_username in client_friend[client_username]:
#         dest_client_socket = clients[dest_client_username][0]
#         send_msg(dest_client_socket, client_socket, data, client_username, dest_client_username)

#    for client_sock, client_addr, _ in clients.values():
 #       if not (sender_client_address[0] == client_addr[0] and sender_client_address[1] == client_addr[1]):
  #          return
            # send_msg(client_sock, data)

# def send_msg(dest_client_socket, client_socket, data, client_username, dest_client_username):
#     if dest_client_username in client_friend[client_username]:
#         dest_client_socket.send(bytes(data, "utf-8"))
#     else:
#         client_socket.send(bytes(f"notFriend||{dest_client_username}", "utf-8"))

# def add_friend_req(client_username, new_friend, client_socket, new_friend_socket):
    # if new_friend not in client_friend[client_username]:

    #     if new_friend in client_friend_request[client_username]:
    #         client_friend_request[client_username].remove(new_friend)
        
    #     if client_username in client_friend_request[new_friend]:
    #         client_friend_request[new_friend].remove(client_username)
        
    #     client_friend[client_username].append(new_friend)
    #     client_friend[new_friend].append(client_username)

    #     client_socket.send(bytes(f"acceptedRequest||{new_friend}", "utf-8"))
    #     new_friend_socket.send(bytes(f"acceptedRequest||{client_username}", "utf-8"))

# def add_friend(client_username, new_friend, client_socket, new_friend_socket):
#     # check kalo udah temenan
#     if new_friend in client_friend[client_username]:
#         client_socket.send(bytes(f"friendExist||{new_friend}", "utf-8"))
#         return

#     if new_friend in client_friend_request[client_username]:
#         add_friend(client_username, new_friend, client_socket, new_friend_socket)
#     # check kalo udah ngirim friend request sebelumnya
#     elif client_username in client_friend_request[new_friend]:
#         client_socket.send(bytes(f"requestExist||{new_friend}", "utf-8"))
#     elif client_username not in client_friend_request[new_friend]:
#         #client_friend_request[client_username].append(new_friend)
#         client_friend_request[new_friend].append(client_username)
#         new_friend_socket.send(bytes(f"friendRequest||{client_username}", "utf-8"))

def send_broadcast(client_username, client_socket, dest, args):
    for dest_username in client_friend[client_username]:
        send_msg(client_username, client_socket, dest_username, args)

def send_msg(client_username, client_socket, dest, args):
    dest_username = dest
    dest_socket = clients[dest][0]
    
    if check_if_in_friend_list(client_username, client_socket, dest_username):
        msg = "chat||<{}>: {}".format(client_username, args)
        dest_socket.send(bytes(msg, "utf-8"))

def show_friend_list(client_username, client_socket, dest, args):
    friends = ', '.join(client_friend[client_username])
    friendRequests = ', '.join(client_friend_request[client_username])
    client_socket.send(bytes(f"friendList||{friends}||{friendRequests}", "utf-8"))
    pass

def add_friend(client_username, client_socket, dest, args):
    dest_username = dest
    dest_socket = clients[dest][0]

    # check kalo udah temenan
    if dest_username in client_friend[client_username]:
        client_socket.send(bytes(f"friendExist||{dest_username}", "utf-8"))
        return

    if dest_username in client_friend_request[client_username]:
        accept_friend_req(client_username, client_socket, dest_username, args)
    # check kalo udah ngirim friend request sebelumnya
    elif client_username in client_friend_request[dest_username]:
        client_socket.send(bytes(f"requestExist||{dest_username}", "utf-8"))
    elif client_username not in client_friend_request[dest_username]:
        #client_friend_request[client_username].append(dest_username)
        client_friend_request[dest_username].append(client_username)
        dest_socket.send(bytes(f"friendRequest||{client_username}", "utf-8"))

def accept_friend_req(client_username, client_socket, dest, args):
    dest_username = dest
    dest_socket = clients[dest][0]
    if dest_username in client_friend_request[client_username]:
        if dest_username not in client_friend[client_username]:

            if dest_username in client_friend_request[client_username]:
                client_friend_request[client_username].remove(dest_username)
            
            if client_username in client_friend_request[dest_username]:
                client_friend_request[dest_username].remove(client_username)
            
            client_friend[client_username].append(dest_username)
            client_friend[dest_username].append(client_username)

            client_socket.send(bytes(f"acceptedRequest||{dest_username}", "utf-8"))
            dest_socket.send(bytes(f"acceptedRequest||{client_username}", "utf-8"))
    else:
        client_socket.send(bytes(f"requestNotExist||{dest_username}", "utf-8"))

def send_file(client_username, client_socket, dest, args):
    if check_if_in_friend_list(client_username, client_socket, dest):
        file_size, filename, file_content = args.split("||")
        cur_file_size = int(file_size) - len(file_content)
        while cur_file_size > 0:
            received_data = client_socket.recv(65535)
            file_content += received_data.decode("utf-8")
            cur_file_size -= len(received_data)
        
        dest_socket = clients[dest][0]
        dest_socket.sendall(bytes(f"createFile||{file_size}||{filename}||{file_content}", "utf-8"))

def unfriend(client_username, client_socket, dest, args):
    if check_if_in_friend_list(client_username, client_socket, dest):
        del client_friend[client_username]
        pass

def attempt_send_file(client_username, client_socket, dest, args):
    if check_if_in_friend_list(client_username, client_socket, dest):
        client_socket.send(bytes(f"allowSendFile||{dest}", "utf-8"))

executeable_func = {    # client_username, client_socket, dest, args 
    "bcast": send_broadcast,
    "friendList": show_friend_list,
    "sendFile": send_file,
    "addFriend": add_friend,
    "acceptFriend": accept_friend_req,
    "sendMessage": send_msg,
    "unfriend": unfriend,
    "attemptSendFile": attempt_send_file
}



server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 7777))
server_socket.listen(5)
clients = {}

client_friend = {}

client_friend_request = {}

while True:
    client_socket, client_address = server_socket.accept()
    client_username = client_socket.recv(65535).decode("utf-8")
    print(client_username, " Joined")
    
    client_thread = threading.Thread(target=read_msg, args=(clients, client_socket, client_address, client_username))
    client_thread.start()

    clients[client_username] = (client_socket, client_address, client_thread)
    if client_username not in client_friend.keys():
        client_friend[client_username] = []
        client_friend_request[client_username] = []