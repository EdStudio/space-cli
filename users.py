import json
import requests

class User:
    def __init__(self, userid, username):
        self.userid = userid
        self.username = username
        self.public_key = None

    def set_public_key(self, public_key):
        self.public_key = public_key

    def print(self):
        print(f"- ID : {self.userid}\n- Username : {self.username}\n- Public key : {self.public_key}")

class Users:
    def __init__(self, client):
        self.users = {}
        self.client = client
    
    def add_user(self, user):
        self.users[user.userid] = user
    
    def ask_user_server(self, identifier, identifier_type):
        url = self.client.server + "/profile"
        payload = {
            identifier_type: identifier
        }
        myresponse = requests.get(url, params=payload, cookies=self.client.cookies)
        myjson = json.loads(myresponse.text)
        if myjson["user"] is None or myjson["user"] is False:
            return False
        user_data = myjson["user"]
        user = User(userid=user_data["id"], username=user_data["username"])
        if user_data["public_key"] != None:
            user.set_public_key(user_data["public_key"])
        self.add_user(user)
        return user

    def get_user(self, identifier, identifier_type):
        if identifier in self.users:
            return self.users[identifier]
        return self.ask_user_server(identifier, identifier_type)

    def print_all(self):
        for user_id, user in self.users.items():
            print(f"{user_id} {user.username}")