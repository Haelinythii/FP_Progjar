from item import itemDatabase
from Command_wrapper import Command_Wrapper
import socket, sys, threading, os, pickle

def read_msg(client_socket):
    while True:
        try:
            data = client_socket.recv(65535)
            data = pickle.loads(data)
        except:
            break
        print(data)

        #if len(data) == 0:
        #    break
        # print(data)
        
        command = data.command
        dest = data.dest
        args = data.args

        # command, args = data.split(b"||", 1)
        # command = command.decode("utf-8")
        
        # if command != "createFile":
        #     args = args.decode("utf-8")

        executeable_func[command](dest, args)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(("127.0.0.1", 7777))

username = sys.argv[1]

client_socket.send(bytes(username, "utf-8"))

client_thread = threading.Thread(target=read_msg, args=(client_socket,))
client_thread.start()

def is_dest_self_username(dest):
    if dest == username:
        print("Can't send anything to yourself!")
        return True
    return False

def show_new_friend_request(dest, args):
    print(f"New friend request from {args[0]}")

def show_friend_request_accepted(dest, args):
    print(f"Friend request accepted! You are now friend with {args[0]}")

def show_friend_list(dest, args):
    friends, friendRequests  = args
    print(f"List of friend: {friends}")
    print(f"List of incoming friend request: {friendRequests}")

def show_friend_already_exist(dest, args):
    print(f"{args[0]} is already in your friend list")

def show_friend_request_already_exist(dest, args):
    print(f"You have sent {args[0]} a friend request before, please wait for them to accept your friend request")

def show_not_friend(dest, args):
    print(f"You're not friend with {args[0]} yet or the user does not exist.")

def show_user_not_exist(dest, args):
    print(f"That user does not exist.")

def create_file(dest, args):
    file_size = int(args[0])
    filename = args[1]
    
    with open(file="./" + filename, mode="wb") as file:
        while file_size > 0:
            received_data = client_socket.recv(65535)
            file.write(received_data)
            file_size -= len(received_data)
            print(file_size)
    
    print("File created!")

def allow_send_file(dest, args):
    file_size = args[0]
    filename = args[1]
    file_content = b""

    with open(file="./" + filename, mode="rb") as file:
        file_content = file.read()

    client_socket.sendall(file_content)

    # command_wrapper = Command_Wrapper("sendFile", dest, (file_size, filename))
    # p_command = pickle.dumps(command_wrapper)
    # client_socket.send(p_command)

def request_not_exist(dest, args):
    print(f"You don't have a friend request from {args[0]}")

def unfriend_success(dest, args):
    print(f"You have successfully remove {args[0]} from your friend list")

def unfriend_notification(dest, args):
    print(f"You have been unfriended by {args[0]}")

def receive_message(dest, args):
    print(f"{args[0]}")

def allow_create_file(dest, args):
    command_wrapper = Command_Wrapper("sendFile", dest, None)
    p_command = pickle.dumps(command_wrapper)
    client_socket.send(p_command)
    create_file(dest, args)
    
def heal(dest, args):
    print("You have been healed to max hit point.")

def training_result(dest, args):
    print(args[0])

def hunting_result_success(dest, args):
    print(f"You get {args[1]} {args[0].name}(s)! You take {args[2]} damage!")
    
def hunting_result_fail(dest, args):
    print(f"You died! You lose 1 Level, 1 attack, 1 defense, and 5 HP. You get nothing!")

def craft_success(dest, args):
    print(f"Craft success!")

def craft_fail(dest, args):
    print(f"Craft fail! You don't have enough materials to craft that item")
    
def foraging_result(dest, args):
    print(f"You get {args[1]} {args[0].name} from foraging!")

executeable_func = {    # (dest, args)
    "friendRequest": show_new_friend_request,
    "acceptedRequest": show_friend_request_accepted,
    "friendList": show_friend_list,
    "friendExist": show_friend_already_exist,
    "requestExist": show_friend_request_already_exist,
    "notFriend": show_not_friend,
    "notExist": show_user_not_exist,
    "createFile": create_file,
    "allowSendFile": allow_send_file,
    "requestNotExist": request_not_exist,
    "unfriendSuccess": unfriend_success,
    "unfriendNotif": unfriend_notification,
    "rcvMessage": receive_message,
    "attemptCreateFile": allow_create_file,
    "heal": heal,
    "trainingResult": training_result,
    "huntingResultSuccess" : hunting_result_success,
    "huntingResultFail" : hunting_result_fail,
    "craftSuccess" : craft_success,
    "craftFail" : craft_fail,
    "foragingResult" : foraging_result
}

while True:

    command = input("\nCommand yang tersedia:\nbcast untuk broadcast pesan ke semua teman\naddFriend untuk mengirim request pertemanan\nacceptFriend untuk menerima request pertemanan yang masuk\nfriendList untuk melihat list dari request pertemanan\nsendFile untuk mengirim file ke seorang teman\nsendMessage untuk mengirim pesan ke seorang teman\nMasukkan command: ")

    if command == "sendFile":
        dest = input("Masukkan tujuan pengiriman file: ")
        if is_dest_self_username(dest):
            continue
        
        filename = input("Masukkan nama file: ")

        if not os.path.exists("./" + filename):
            print("File tidak ada.")
        else:
            file_size = os.path.getsize("./" + filename)
            command_wrapper = Command_Wrapper("attemptRecvFile", dest, (file_size, filename))
            p_command = pickle.dumps(command_wrapper)
            client_socket.send(p_command)
        
    elif command == "exit":
        client_socket.close()
        break
    else:
        if command == "friendList":
            dest = "friendList"
            args = "a"
        elif command == "addFriend" or command == "acceptFriend":
            dest = input("Masukkan nama teman anda: ")
            if is_dest_self_username(dest):
                continue
            args = "friend"
        elif command == "sendMessage":
            dest = input("Masukkan tujuan pengiriman pesan: ")
            if is_dest_self_username(dest):
                continue
            args = input("Masukkan pesan anda: ")
        elif command == "bcast":
            dest = "bcast"
            args = input("Masukkan pesan anda: ")
        elif command == "unfriend":
            dest = input("Masukkan nama teman yang ingin di-unfriend: ")
            args = "unfriend"
        elif command == "training" or command == "hunting" or command == "foraging" or command == "heal" or command == "craftingList":
            dest = username
            args = ""
        elif command == "crafting":

            item_database = itemDatabase()
            print("\n\nCrafting List:")
            for category in item_database.craftable_category:
                modifier_name = ""
                
                if list(category.values())[0].category == "weapon":
                    print("\nCrafting List for weapon: ")
                    modifier_name = "ATK"
                elif list(category.values())[0].category == "armor":
                    print("\nCrafting List for armor: ")
                    modifier_name = "DEF"

                for key, value in category.items():
                    crafting_materials = []
                    for crafting_material in value.crafting_material:
                        crafting_materials.append(f"{crafting_material[1]} {crafting_material[0].name}")
                    
                    needed_material = ", ".join(crafting_materials)
                    print(f"{key} ({value.modifier} {modifier_name}) -> {needed_material}")

            dest = username
            nama_item = input("Masukkan nama item yang ingin di craft: ")
            args = item_database.equipment[nama_item] 
        else:
            print("Command tidak tersedia.")
            continue
        command_wrapper = Command_Wrapper(command, dest, (args,))
        p_command = pickle.dumps(command_wrapper)
        client_socket.send(p_command)