#db.py
# File to connect to Mongodb Atlas

from flask import Flask
from flask_pymongo import pymongo
CONNECTION_STRING = "mongodb+srv://<username>:<password>@cluster0.rsgu3br.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('database_name')
user_collection = pymongo.collection.Collection(db, 'collection_name')
