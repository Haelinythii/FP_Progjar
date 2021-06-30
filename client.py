from Command_wrapper import Command_Wrapper
import socket, sys, threading, os, pickle


def read_msg(client_socket):
    while True:
        try:
            data = client_socket.recv(65535)
        except:
            break
        print(data)

        #if len(data) == 0:
        #    break
        # print(data)
        
        command, args = data.split(b"||", 1)
        command = command.decode("utf-8")
        
        if command != "createFile":
            args = args.decode("utf-8")

        executeable_func[command](args)

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

def show_new_friend_request(args):
    print(f"New friend request from {args}")

def show_friend_request_accepted(args):
    print(f"Friend request accepted! You are now friend with {args}")

def show_friend_list(args):
    friends, friendRequests  = args.split('||', 1)
    print(f"List of friend: {friends}")
    print(f"List of incoming friend request: {friendRequests}")

def show_friend_already_exist(args):
    print(f"{args} is already in your friend list")

def show_friend_request_already_exist(args):
    print(f"You have sent {args} a friend request before, please wait for them to accept your friend request")

def show_not_friend(args):
    print(f"You're not friend with {args} yet or the user does not exist.")

def show_user_not_exist(args):
    print(f"That user does not exist.")

def create_file(args):
    file_size, filename, file_content = args.split(b"||")
    file_size = int(file_size.decode("utf-8"))
    filename = filename.decode("utf-8")
    with open(file="./" + filename, mode="wb") as file:
        file.write(file_content)
        file_size -= len(file_content)

        while file_size > 0:
            received_data = client_socket.recv(65535)
            file.write(received_data)
            file_size -= len(received_data)

    print("File created!")

def allow_send_file(args):
    filename = input("Masukkan nama file: ")

    if not os.path.exists("./" + filename):
        print("File tidak ada.")
    else:
        file_content = b""
        file_size = 0

        with open(file="./" + filename, mode="rb") as file:
            file_content = file.read()
            file_size = len(file_content)
        
        client_socket.sendall(bytes(f"sendFile||{args}||{file_size}||{filename}||", "utf-8") + file_content)

def request_not_exist(args):
    print(f"You don't have a friend request from {args}")

executeable_func = {    # (args)
    "friendRequest": show_new_friend_request,
    "acceptedRequest": show_friend_request_accepted,
    "friendList": show_friend_list,
    "friendExist": show_friend_already_exist,
    "requestExist": show_friend_request_already_exist,
    "notFriend": show_not_friend,
    "notExist": show_user_not_exist,
    "createFile": create_file,
    "allowSendFile": allow_send_file,
    "requestNotExist": request_not_exist
}

while True:

    command = input("\nCommand yang tersedia:\nbcast untuk broadcast pesan ke semua teman\naddFriend untuk mengirim request pertemanan\nacceptFriend untuk menerima request pertemanan yang masuk\nfriendList untuk melihat list dari request pertemanan\nsendFile untuk mengirim file ke seorang teman\nsendMessage untuk mengirim pesan ke seorang teman\nMasukkan command: ")

    if command == "sendFile":
        dest = input("Masukkan tujuan pengiriman file: ")
        if is_dest_self_username(dest):
            continue
        
        command_wrapper = Command_Wrapper(command, (dest, None))
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
        else:
            print("Command tidak tersedia.")
            continue
        command_wrapper = Command_Wrapper(command, (dest, args))
        client_socket.send(bytes(f"{command}||{dest}||{args}", "utf-8"))