import requests
import json

class Client:
    def __init__(self):
        self.server = None
        self.username = None
        self.cookies = None
        self.id = None
    
    def auth(self, server, username, password):
        url = server + "/auth"
        payload = {
            "username": username,
            "password": password
        }
        myresponse = requests.post(url, data=payload)
        myjson = json.loads(myresponse.text)
        if myjson.get("auth", False) is False or myjson.get("auth") is None:
            return False
        self.id = myjson["auth"]["id"]
        self.username = myjson["auth"]["username"]
        self.cookies = myresponse.cookies.get_dict()
        print(self.cookies)
        self.server = server
        return True