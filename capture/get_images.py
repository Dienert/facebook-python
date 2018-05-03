from pymongo import MongoClient
import urllib.request
import base64
import os

client = MongoClient('localhost', 27017)
db = client.facebook
db_name = "Diénert Vieira"
#db_name = "Josirene Alencar"
friends_collection = db[db_name]
#friends_collection = db["User Name"]
friends = friends_collection.find({}, {"_id": 0, "name": 1, "id": 1, "image": 1})

path_root = "../visualization/fotos/"+db_name+"/"
os.mkdir(path_root)

for friend in friends:
    path = path_root+friend["name"]+"_"+friend["id"]+".jpg"
    urllib.request.urlretrieve (friend['image'], path)
    #image_file = open(path, "rb")
    #encoded_string = base64.b64encode(image_file.read())
    #print(encoded_string)
    #exit()