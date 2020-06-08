if __name__ in ["__main__", "identity_test"]:
  import sys
  sys.path.append('..')
  from identity import *
else:
  from ..identity import * # this line not tested, could be buggy

def is_mongo_installed_in_localhost():
  import pymongo
  try: pymongo.MongoClient("mongodb://localhost:27017/").list_database_names()
  except pymongo.errors.ServerSelectionTimeoutError:
    print('Error: MongoDB not installed on localhost:27017')
  except:
    print('Error: MongoDB cannot be accessed')


  


all_test = [
  is_mongo_installed_in_localhost,
]


if __name__ in ["__main__", "identity_test"]:
  for f in all_test:
    f()
