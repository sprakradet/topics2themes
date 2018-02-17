import pymongo
import datetime
from pymongo import MongoClient



class MongoConnector:
    def __init__(self):
        #self.TOPIC_MODEL_DATABASE = "topic_model_database"
        self.TOPIC_MODEL_DATABASE = "text_database"
        self.client = None
        self.DATE = "date"
        self.ID = "_id"
        self.TOPIC_ID = "topic_id"
        self.TOPIC_NAME = "topic_name"
        self.MODEL_ID = "model_id"
        self.TOPIC_MODEL_OUTPUT = "topic_model_output"
        self.TEXT_COLLECTION_NAME = "text_collection_name"
    
    def get_connection(self):
        maxSevSelDelay = 5 #Check that the server is listening, wait max 5 sec
        if not self.client:
            self.client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=maxSevSelDelay)
        self.server_info = self.client.server_info()
        return self.client
    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None

    def get_database(self):
        con = self.get_connection()
        db = con[self.TOPIC_MODEL_DATABASE]
        return db

    ### Storing and fetching the output of models
    def get_model_collection(self):
        db = self.get_database()
        model_collection = db["MODEL_COLLECTION"]
        return model_collection
    
    def get_all_model_document_name_date_id(self):
        documents = self.get_model_collection().find()
        document_spec = [{self.DATE: document['_id'].generation_time,\
                         self.TEXT_COLLECTION_NAME: document[self.TEXT_COLLECTION_NAME],\
                         self.ID : document[self.ID]}\
                         for document in documents]
        return document_spec
    
    def get_topic_model_output_with_id(self, id):
        document = self.get_model_collection().find_one({ self.ID : id})
        return document[self.TOPIC_MODEL_OUTPUT]
    
    def get_all_collections(self):
        return self.get_database().collection_names()

    def insert_new_model(self, topic_model_output, text_collection_name):
        time = datetime.datetime.utcnow()
        post = {self.TEXT_COLLECTION_NAME : text_collection_name,\
                self.TOPIC_MODEL_OUTPUT: topic_model_output}
        post_id = self.get_model_collection().insert_one(post).inserted_id
        return time, post_id

    ### Storing and fetching names of topics

    def get_topic_name_collection(self):
        db = self.get_database()
        topic_name_collection = db["TOPIC_NAME_COLLECTION"]
        return topic_name_collection

    def save_or_update_topic_name(self, topic_id, new_name, model_id):
        current_post = self.get_topic_name_collection().find_one({self.TOPIC_ID : topic_id,\
                                                  self.MODEL_ID : model_id})
        print(current_post)
        if not current_post:
            post = {self.TOPIC_ID : topic_id, self.MODEL_ID : model_id, self.TOPIC_NAME : new_name}
            post_id = self.get_topic_name_collection().insert_one(post).inserted_id
            return post
        else:
            print("exist")
            
            self.get_topic_name_collection().update_one({self.ID : current_post[self.ID]},\
                                                        {"$set": { self.TOPIC_NAME : new_name }})
            return self.get_topic_name_collection().find_one({self.TOPIC_ID : topic_id,\
                                                        self.MODEL_ID : model_id})


###

###
# Start
###
if __name__ == '__main__':
    mc = MongoConnector()
    print(mc.get_connection())
    print(mc.get_database())
    print(mc.get_all_collections())
    #print(mc.insert_new_model("test", "name"))
    #print(mc.get_all_collections())

    els = mc.get_all_model_document_name_date_id()
    for el in els:
        print("****************")
        print(el)
        print(str(el[mc.DATE]))
        print(mc.get_topic_model_output_with_id(el[mc.ID]))
        print()
      
    print(mc.save_or_update_topic_name("topc id test", "new name text", "model id test"))
    print(mc.save_or_update_topic_name("topc id test", "updated name text", "model id test"))
    """
        print(p["text_collection_name"])
        print()
        print(p["date"])
        print()
     """
#print(p["topic_model_output"])


    mc.close_connection()
    print(mc.get_all_collections())
