from pymongo import MongoClient
from bson.json_util import dumps
import io
import re

client = MongoClient('localhost', 27017)
db = client.facebook
friends_collection = db["User Name"]

idiom = "pt-br"
#idiom = "en"

terms = { "en" : {"female": "Female",   "male": "Male",      "single-f": "Solteira", "single-m": "Solteiro" }, 
        "pt-br": {"female": "Feminino", "male": "Masculino", "single-f": "Single",   "single-m": "Single"} }

mulheres = {"genero": terms[idiom]["female"]}
mulheres_solteiras = {"$or": [{"genero": terms[idiom]["female"], "status": "-"},
                              {"genero": terms[idiom]["female"], "status":  terms[idiom]["single-f"]},
                              {"genero" : { "$exists" : False }, "status": "-"}]}

homens = {"genero": terms[idiom]["male"]}
homens_solteiros = {"$or": [{"genero": terms[idiom]["male"], "status": "-"},
                              {"genero": terms[idiom]["male"], "status": terms[idiom]["single-m"]},
                              {"genero" : { "$exists" : False }, "status": "-"}]}

todos_solteiros = {"status": "Single"}
todos_sem_status = {"status": "-"}
#query = mulheres
#query = homens
#query = homens_solteiros
query = mulheres_solteiras
#query = todos_solteiros
#query = todos_sem_status
#query = {}

ids = friends_collection.find(query, {"_id": 0, "id": 1})
ids = [id["id"] for id in ids]

nodes = friends_collection.find(query, {"_id": 0, "links": 0})
friends_file = io.open('../visualization/test.json', mode='w', encoding='utf-8')
friends_file.write("{\n\t\t\"nodes\": \n")
json = re.sub("},","},\n", dumps(nodes))
friends_file.write(json)

links = friends_collection.find(query, {"_id": 0, "id": 1, "links": 1, "nome": 1})

friends_file.write(",\n\t\t\"links\": [\n")
primeiro = True
for friend in links:
    if "links" in friend:
        for index, link in enumerate(friend["links"]):
            if link in ids:
                if not primeiro:
                    friends_file.write(",\n")
                friends_file.write('{"source": "'+friend["id"]+'","target":"'+link+'"}')
                primeiro = False
friends_file.write("\n]}")
friends_file.close()