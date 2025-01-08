from pymongo import MongoClient

from config import DB_NAME, MONGO

client = MongoClient(MONGO)

users = client[DB_NAME]['users']
groups = client[DB_NAME]['groups']
delay = client[DB_NAME]['delay']

def already_db(user_id):
    user = users.find_one({"user_id" : str(user_id)})
    if not user:
        return False
    return True

def already_dbg(chat_id):
    group = groups.find_one({"chat_id" : str(chat_id)})
    if not group:
        return False
    return True

def add_user(user_id):
    in_db = already_db(user_id)
    if in_db:
        return
    return users.insert_one({"user_id": str(user_id)}) 

def remove_user(user_id):
    in_db = already_db(user_id)
    if not in_db:
        return 
    return users.delete_one({"user_id": str(user_id)})
    
def add_group(chat_id):
    in_db = already_dbg(chat_id)
    if in_db:
        return
    return groups.insert_one({"chat_id": str(chat_id)})

def all_users():
    user = users.find({})
    usrs = len(list(user))
    return usrs

def all_groups():
    group = groups.find({})
    grps = len(list(group))
    return grps

def get_all_peers():
    Users = users.find({})
    if Users:
        peers = [int(i["user_id"]) for i in list(Users)]
    else:
        peers = None
    return peers

def add_accept_delay(chat: int, time: int):
    already = delay.find_one({"chat_id": chat})
    if already:
        delay.update_one({"chat_id": chat}, {"delay": time})
        return already["delay"]
    else:
        delay.insert_one({"chat_id": chat, "delay": time})
        return time

def get_adelay(chat: int):
    Delay = delay.find_one({"chat_id": chat})
    return Delay["delay"] if Delay else None