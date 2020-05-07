import pymongo

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
yay_db = mongo_client["yay-db"]

test_collection = yay_db["test"]

mydict = { "name": "Peter", "address": "Lowstreet 27" }

x = test_collection.insert_one(mydict)

print(x.inserted_id)

y = test_collection.find_one()

print(y)