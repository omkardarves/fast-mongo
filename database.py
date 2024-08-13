import pymongo

url = 'mongodb://localhost:27017'

client = pymongo.MongoClient(url)
db = client.fast_test
collection_name = db["todo_collection"]

try:
    client.admin.command("ping")
    print("Ping successful")
except Exception as e:
    print(e)