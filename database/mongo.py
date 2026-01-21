import os
import certifi

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing import Optional

from rich.console import Console

client: Optional[AsyncMongoClient] = None
db: AsyncDatabase = None
console = Console()

async def connect_db():

    uri = os.getenv("DB_TOKEN")
    global db
    
    try:
        client = AsyncMongoClient(
            uri,
            serverSelectionTimeoutMS=3000,  # ⬅ VERY IMPORTANT
            connectTimeoutMS=3000,
            socketTimeoutMS=3000,
            maxPoolSize=100,
            minPoolSize=10,
            tls=True,
            tlsCAFile=certifi.where()
        )

        db = client.get_database("mikontrol")
    
    
        await client.admin.command('ping')
        console.log("Connected to MongoDB successfully!")
    except Exception as e:
        console.log(f"Error connecting to MongoDB: {e}")

def get_db() -> AsyncDatabase:
    if db is None:
        raise Exception("Database not connected. Call connect_db() first.")
    return db

async def close_mongo():
    if client is not None:
        await client.close()
        
