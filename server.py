from item import itemDatabase
from player import Player
from inventory import inventory
import socket, threading, pickle, random
from Command_wrapper import Command_Wrapper

file_data_to_be_sent = {}

def read_msg(clients, client_socket, client_address, client_username):
    while True:
        try:
            data = client_socket.recv(65535)
            data = pickle.loads(data)
        except:
            del clients[client_username]
            break        
        
        command = data.command
        dest = data.dest
        args = data.args

        print(command)

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
        send_pickle("notExist", None, (dest,), client_socket)
        # client_socket.send(bytes(f"notExist||{dest}", "utf-8"))
        return False

def check_if_in_friend_list(client_username, client_socket, dest):
    if dest not in client_friend[client_username]:
        send_pickle("notFriend", None, (dest,), client_socket)
        # client_socket.send(bytes(f"notFriend||{dest}", "utf-8"))
        return False
    return True

def send_broadcast(client_username, client_socket, dest, args):
    for dest_username in client_friend[client_username]:
        send_msg(client_username, client_socket, dest_username, args)

def send_msg(client_username, client_socket, dest, args):
    dest_username = dest
    dest_socket = clients[dest][0]
    
    if check_if_in_friend_list(client_username, client_socket, dest_username):
        msg = "<{}>: {}".format(client_username, args[0])
        send_pickle("rcvMessage", None, (msg,), dest_socket)
        # dest_socket.send(bytes(msg, "utf-8")) ################################################

def show_friend_list(client_username, client_socket, dest, args):
    friends = ', '.join(client_friend[client_username])
    friendRequests = ', '.join(client_friend_request[client_username])
    send_pickle("friendList", None, (friends, friendRequests), client_socket)
    pass

def add_friend(client_username, client_socket, dest, args):
    dest_username = dest
    dest_socket = clients[dest][0]

    # check kalo udah temenan
    if dest_username in client_friend[client_username]:
        send_pickle("friendExist", None, (dest_username,), client_socket)
        return

    if dest_username in client_friend_request[client_username]:
        accept_friend_req(client_username, client_socket, dest_username, args)
    # check kalo udah ngirim friend request sebelumnya
    elif client_username in client_friend_request[dest_username]:
        send_pickle("requestExist", None, (dest_username,), client_socket)
    elif client_username not in client_friend_request[dest_username]:
        #client_friend_request[client_username].append(dest_username)
        client_friend_request[dest_username].append(client_username)
        send_pickle("friendRequest", None, (client_username,), dest_socket)

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

            send_pickle("acceptedRequest", None, (dest_username,), client_socket)
            send_pickle("acceptedRequest", None, (client_username,), dest_socket)
    else:
        send_pickle("requestNotExist", None, (dest_username,), client_socket)

def recv_file(client_username, client_socket, dest, args):
    
    # with open(file="./temp", mode="wb") as file:
    received_data = client_socket.recv(65535)
    file_data_to_be_sent[dest] = received_data
    file_size = int(args[0]) - len(received_data)
    while file_size > 0:
        received_data = client_socket.recv(65535)
        file_data_to_be_sent[dest] += received_data
        file_size -= len(received_data)
    
    attempt_send_file(client_username, client_socket, dest, args)

def send_file(client_username, client_socket, dest, args):
    file_content = file_data_to_be_sent[client_username]
    client_socket.sendall(file_content)
    del file_data_to_be_sent[client_username]

    # print(file_content)

    # file_size, filename, file_content = args
    # cur_file_size = int(file_size) - len(file_content)
    # while cur_file_size > 0:
    #     received_data = client_socket.recv(65535)
    #     file_content += received_data.decode("utf-8")
    #     cur_file_size -= len(received_data)
    
    # dest_socket = clients[dest][0]
    # command_wrapper = Command_Wrapper("createFile", None, (file_size, filename, file_content))
    # p_command = pickle.dumps(command_wrapper)
    # dest_socket.sendall(p_command)
    # dest_socket.sendall(bytes(f"createFile||{file_size}||{filename}||{file_content}", "utf-8"))

def unfriend(client_username, client_socket, dest, args):
    if check_if_in_friend_list(client_username, client_socket, dest):
        
        client_friend[client_username].remove(dest)
        client_friend[dest].remove(client_username)
        send_pickle("unfriendSuccess", None, (dest,), client_socket)
        send_pickle("unfriendNotif", None, (client_username,), clients[dest][0])

def attempt_recv_file(client_username, client_socket, dest, args):
    print(args)
    if check_if_in_friend_list(client_username, client_socket, dest):
        send_pickle("allowSendFile", dest, args, client_socket)
        recv_file(client_username, client_socket, dest, args)
        # client_socket.send(bytes(f"allowSendFile||{dest}", "utf-8"))

def attempt_send_file(client_username, client_socket, dest, args):
    dest_socket = clients[dest][0]
    send_pickle("attemptCreateFile", dest, args, dest_socket)
    
def training(client_username, client_socket, dest, args):
    exp = random.randint(1, 15)
    player_object = client_player_object[client_username]
    if player_object.training(exp):
        msg = f"You get {exp} experience! Level up to level {player_object.get_level()}!"
    else:
        msg = f"You get {exp} experience!"
    send_pickle("trainingResult", None, (msg,), client_socket)

def hunting(client_username, client_socket, dest, args):
    
    damage = random.randint(10, 50)
    is_player_dead = client_player_object[client_username].take_damage_hunting(damage)
    
    if not is_player_dead:
        item_amount = random.randint(1, 3)
        hunting_material = item_database.getHuntingMaterial()
        item = hunting_material[random.randint(0, len(hunting_material) - 1)]

        client_player_object[client_username].inventory.store(item, item_amount)
        print(client_player_object[client_username].inventory.list_item[item.name])
        send_pickle("huntingResultSuccess", None, (item, item_amount, damage,), client_socket)
    else:
        send_pickle("huntingResultFail", None, None, client_socket)

def crafting(client_username, client_socket, dest, args):
    can_craft = True
    item = args[0]

    for i in item.crafting_material:
        if client_player_object[client_username].inventory.get_item_amount(i[0]) < i[1]:
            can_craft = False
            break
    
    if can_craft:
        for i in item.crafting_material:
            client_player_object[client_username].inventory.remove_item(i[0], i[1])
        
        if item.category == "weapon":
            client_player_object[client_username].set_weapon(item)
            print(client_player_object[client_username].get_damage())
        elif item.category == "armor":
            client_player_object[client_username].set_armor(item)
        send_pickle("craftSuccess", None, None, client_socket)
    else:
        send_pickle("craftFail", None, None, client_socket)

def foraging(client_username, client_socket, dest, args):
    # damage = random.randint(10, 50)
    # is_player_dead = client_player_object[client_username].take_damage_hunting(damage)
    
    item_amount = 1
    foraging_material = item_database.getForagingMaterial()
    item = foraging_material[random.randint(0, len(foraging_material) - 1)]
    client_player_object[client_username].inventory.store(item, item_amount)
    send_pickle("foragingResult", None, (item, item_amount,), client_socket)

def heal(client_username, client_socket, dest, args):
    client_player_object[client_username].heal()
    send_pickle("heal", None, None, client_socket)

executeable_func = {    # client_username, client_socket, dest, args 
    "bcast": send_broadcast,
    "friendList": show_friend_list,
    "sendFile": send_file,
    "addFriend": add_friend,
    "acceptFriend": accept_friend_req,
    "sendMessage": send_msg,
    "unfriend": unfriend,
    "attemptRecvFile": attempt_recv_file,
    "attemptSendFile": attempt_send_file,
    "training" : training,
    "hunting" : hunting,
    "crafting" : crafting,
    "foraging" : foraging,
    "heal" : heal,
}

def send_pickle(command, dest, args, socket):
    command_wrapper = Command_Wrapper(command, dest, args)
    p_command = pickle.dumps(command_wrapper)
    socket.send(p_command)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 7777))
server_socket.listen(5)
clients = {}

client_friend = {}

client_friend_request = {}

client_player_object = {}

item_database = itemDatabase()

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
        client_player_object[client_username] = Player(100, 0, 5, 2, 3, inventory({}, item_database))