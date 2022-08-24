#db.py
# File to connect to Mongodb Atlas

from flask import Flask
from flask_pymongo import pymongo
CONNECTION_STRING = "mongodb+srv://ZaheedaT:Hamza%40959@cluster0.rsgu3br.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('aizatrondb')
user_collection = pymongo.collection.Collection(db, 'flask-mongodb-atlas')