import argparse
import requests
import json
import datetime
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

from client import Client
from users import Users
from talk import Talk
from commands import Commands

def print_acc_timestamp(string_timestamp):
    timestamp = datetime.datetime.strptime(string_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    if timestamp.date() == datetime.datetime.now().date():
        return(timestamp.strftime("%H:%M"))
    elif timestamp.date() == yesterday.date():
        return "Yesterday"
    elif timestamp.year == datetime.datetime.now().year:
        return(timestamp.strftime("%d %b"))
    else:
        return(timestamp.strftime("%Y"))

def cmd_message(cmd):
    if len(cmd) < 3:
        print("usage: message <user> <message>")
        return
    user = users.get_user(cmd[1], "username")
    if user == False:
        print("User not found")
        return
    message = " ".join(cmd[2:])
    users_list = [client.id, user.userid]
    message_list = []
    for i in range(len(users_list)):
        public_key = users.get_user(users_list[i], "id").public_key
        if public_key == None:
            print(f"User {users_list[i]} does not have a public key")
            return
        current_message = talk.encrypt(message, public_key)
        message_list.append({
            "userid": users_list[i],
            "message": current_message
        })

    #public_key = user.public_key
    #is_encrypted = "false"
    #if public_key == None:
    #    result = None
    #    while result != "y" and result != "n":
    #        result = input("User does not have a public key, send anyway? (y/n) ")
    #    if result == "n":
    #        return
    #message = talk.encrypt(message)
    #return
    is_encrypted = True
    url = client.server + "/message"
    payload = {
        "userid": int(user.userid),
        "message": message_list,
        "is_encrypted": is_encrypted
    }
    response = requests.post(url, json=payload, cookies=client.cookies)
    print(response.text)

def cmd_conv(cmd):
    if len(cmd) < 2:
        print("usage: conv <user>")
        return
    url = client.server + "/messages"
    payload = {
        "user": cmd[1]
    }
    myresponse = requests.get(url, params=payload, cookies=client.cookies)
    myjson = json.loads(myresponse.text)
    if myjson["messages"] == None:
        print("No messages")
        return
    userid1 = client.id
    userid2 = int(cmd[1]) 
    username1 = client.username
    username2 = users.get_user(userid2, "id").username
    for message in myjson["messages"]:
        is_encrypted = message["is_encrypted"]
        msg_if_encrypted = "▢"
        if is_encrypted:
            msg_if_encrypted = f"{Fore.CYAN}▢{Style.RESET_ALL}"
            message['message'] = talk.decrypt(message['message'])
        show_timestamp = print_acc_timestamp(message["created_at"])
        if message["from_user_id"] == userid1:
            print(f"{msg_if_encrypted}  {show_timestamp} {Fore.MAGENTA}{username1}{Style.RESET_ALL} {message['message']}")
            continue
        if message["from_user_id"] == userid2:
            print(f"{msg_if_encrypted}  {show_timestamp} {Fore.CYAN}{username2}{Style.RESET_ALL} {message['message']}")
            continue
        userid3 = message["from_user_id"]
        username3 = users.get_user(userid3, "id").username
        if username3 == False:
            username3 = str(userid3)
        print(f"{msg_if_encrypted}  {show_timestamp} {Fore.RED}{username3}{Style.RESET_ALL} {message['message']}")

def cmd_info(cmd):
    if cmd[1] == "all":
        users.print_all()
        return
    if len(cmd) < 3:
        print("usage: info <username/id/all> <field>")
        return
    elif cmd[1] == "username":
        myuser = users.get_user(cmd[2], "username")
        if myuser:
            myuser.print()
    elif cmd[1] == "id":
        myuser = users.get_user(cmd[2], "id")
        if myuser:
            myuser.print()
    else:
        print("invalid field")

parser = argparse.ArgumentParser()
parser.add_argument("--server", help="server address", default="http://localhost:3000")
parser.add_argument("--username", help="username", required=True)
parser.add_argument("--password", help="password", required=True)
args = parser.parse_args()

client = Client()
result = client.auth(args.server, args.username, args.password)
if not result or not client.username:
    print("Authentication failed.")
    exit(1)
print("Conneted as " + client.username)
users = Users(client)
talk = Talk(client.username)
talk.load_keys()
talk.send_public_key(client)
commands = Commands()
while True:
    cmd = input("space> ").split()
    if len(cmd) == 0:
        continue
    if cmd[0] == "quit":
        break
    elif cmd[0] == "message":
        cmd_message(cmd)
    elif cmd[0] == "conv":
        cmd_conv(cmd)
    elif cmd[0] == "help":
        commands.help()
    elif cmd[0] == "info":
        cmd_info(cmd)
    else:
        print(cmd[0] + " is not a valid command")
