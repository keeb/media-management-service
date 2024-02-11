from pymongo import MongoClient

client = MongoClient("mongodb://treehouse:mongo@localhost:27017")
db = client.mm
collection = db.new 

pipeline = [
    {"$unwind": "$show"},
    {"$group": {"_id": "$show.magnet", "shows": {"$addToSet": "$show"}}},
    {"$project": {"_id": 0, "shows": 1}}
]

result = list(collection.aggregate(pipeline))

print (len(result))