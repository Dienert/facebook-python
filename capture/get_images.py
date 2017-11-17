from pymongo import MongoClient
import urllib.request
import base64

client = MongoClient('localhost', 27017)
db = client.facebook
friends_collection = db["User Name"]
friends = friends_collection.find({}, {"_id": 0, "name": 1, "id": 1, "image": 1})

for friend in friends:
    path = "../visualization/fotos/"+friend["name"]+"_"+friend["id"]+".jpg"
    urllib.request.urlretrieve (friend['image'], path)
    #image_file = open(path, "rb")
    #encoded_string = base64.b64encode(image_file.read())
    #print(encoded_string)
    #exit()