from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from datetime import datetime
import streamlit as st

def get_mongo_client(connection_string):
    return MongoClient(connection_string, server_api=ServerApi('1'))

def check_identifier(connection_string, identifier):
    """Check if the identifier exists in the valid_identifiers collection."""
    client = get_mongo_client(connection_string)
    db = client.embot
    try: 
        result = db.valid_identifiers.find_one({"identifier": identifier})
        return bool(result)
    finally:
        client.close()

def log_transcript(connection_string, conversation_type, messages):
    client = get_mongo_client(connection_string)
    db = client["embot"]
    collection = db["transcriptsWk4"]

    try:
        # Create new document for previous conversation
        document = {
            "timestamp": datetime.utcnow(),
            "em_messages": messages,
            "identifier": st.session_state.get("user_identifier", "anonymous")
        }
        result = collection.insert_one(document)
        return str(result.inserted_id)
        
    finally:
        client.close()
