import hmac
import logging
from random import randint

SECRET = 278312

def hash_str(s):
    return str(hmac.new(str(s)).hexdigest())
def make_secure_value(s):
    return str(s) + "|" + str(hmac.new(str(s), str(SECRET)).hexdigest())
def check_secure_value(h):
    tohash = h.split("|")
    if (make_secure_value(tohash[0]) == h):
        return tohash[0]
    else:
        return None
def make_salt():
    salt = ""
    for i in range(0, 25):
        salt += chr(randint(65, 122))
    return salt
def make_pw_hash(name, pw, salt=None):
    if (salt == None):
        salt = make_salt()
        return str(hash_str(str(name) + str(pw) + str(salt))) + "|" + salt
    else:
        return hash_str(str(name) + str(pw) + salt) + "|" + salt
def valid_pw(name, pw, h):
    salt = h.split("|")[1]
    print(make_pw_hash(name, pw, salt) + " is the hash val")
    if (make_pw_hash(name, pw, salt) == h):
        return True
    else:
        return False
