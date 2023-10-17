import rsa
import requests
import json
import os

class Talk:
    def __init__(self, username):
        self.public_key = None
        self.private_key = None
        self.public_key_path = 'keys/' + username.lower() + '.pub'
        self.private_key_path = 'keys/' + username.lower() + '.priv'

    def load_keys(self):
        if not os.path.isfile(self.public_key_path) or not os.path.isfile(self.private_key_path):
            result = None
            while result != "y" and result != "n":
                result = input("No keys found in keys folder, generate new keys? (y/n) ")
            if result == "n":
                exit(1)        
            self.generate_keys()
        with open(self.public_key_path, mode='rb') as publicfile:
            self.public_key = rsa.PublicKey.load_pkcs1(publicfile.read())
        with open(self.private_key_path, mode='rb') as privatefile:
            self.private_key = rsa.PrivateKey.load_pkcs1(privatefile.read())

    def generate_keys(self):
        self.public_key, self.private_key = rsa.newkeys(1024)
        with open(self.public_key_path, mode='wb') as publicfile:
            publicfile.write(self.public_key.save_pkcs1())
        with open(self.private_key_path, mode='wb') as privatefile:
            privatefile.write(self.private_key.save_pkcs1())

    def encrypt(self, message, public_key):
        data = public_key.encode()
        data = b'-----BEGIN RSA PUBLIC KEY-----\n' + data + b'\n-----END RSA PUBLIC KEY-----'
        public_key = rsa.PublicKey.load_pkcs1(data)
        message = message.encode()
        result = rsa.encrypt(message, public_key)
        result = result.hex()
        return result

    def decrypt(self, message):
        result = rsa.decrypt(bytes.fromhex(message), self.private_key)
        result = result.decode()
        return result
    
    def send_public_key(self, client):
        cookie = client.cookies
        url = client.server + "/public_key"
        payload = {
            "public_key": self.get_own_public_key()
        }
        myresponse = requests.post(url, data=payload, cookies=cookie)
        myjson = json.loads(myresponse.text)

        if myjson["isUpdated"] == False or myjson["isUpdated"] == None:
            return False
        return True

    def get_own_public_key(self, formated=True):
        data = self.public_key.save_pkcs1(format='PEM')
        if formated:
            data = data.decode('utf-8')
            data = data.replace('-----BEGIN RSA PUBLIC KEY-----', '')
            data = data.replace('-----END RSA PUBLIC KEY-----', '')
            data = data.replace('\n', '')
        return data


#talk = Talk()
#talk.load_keys()
#talk.share_public_key()

#message = "Hi my name is Enzo"
#encrypted = talk.encrypt(message)
#rint(encrypted)
#decrypted = talk.decrypt(encrypted)
#print(decrypted)
