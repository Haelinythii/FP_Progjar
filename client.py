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
        else:
            print("Command tidak tersedia.")
            continue
        command_wrapper = Command_Wrapper(command, dest, (args,))
        p_command = pickle.dumps(command_wrapper)
        client_socket.send(p_command)