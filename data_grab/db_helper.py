import pymongo

connection = pymongo.MongoClient('localhost', 27017, maxPoolSize=10)
# mydb_list = [connection.myproject1,connection.myproject2,connection.myproject3,connection.myproject4,connection.myproject5]
mydb_list = connection.myproject
