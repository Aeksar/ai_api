from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
from typing import List, Union
import os
from dotenv import load_dotenv


class Mongo:
    def __init__(self):
        load_dotenv()
        self.uri = os.environ.get('URI')
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client['prompt']


    async def insert_prompt(self, chat_id: Union[int, str], role: str, message: str) -> bool:
        data = {
            "role": role,
            "content": message,
            "created_at": datetime.now()
            }
         
        collection = self.db[str(chat_id)]
        await collection.insert_one(data)
        return True

    async def get_prompt(self, chat_id: Union[str, int]):
        collection = self.db[str(chat_id)]
        
        del_time = datetime.now() - timedelta(days=30)
        collection.delete_many({"created_at": {"$lt": del_time}})
        
        cursor = collection.find({}, {"role": 1, "content": 1}).sort("created_at", 1)
        docs = await cursor.to_list(length=None)
        
        if len(docs) > 1000:
            for doc in docs[:-1000]:
                await collection.delete_one({"_id": doc["_id"]})
        return docs