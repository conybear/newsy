from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "acta_diurna")

class Database:
    client: AsyncIOMotorClient = None
    db = None

database = Database()

async def connect_to_mongo():
    """Create database connection"""
    database.client = AsyncIOMotorClient(MONGO_URL)
    database.db = database.client[DB_NAME]
    
    # Create indexes for better performance
    await database.db.users.create_index("email", unique=True)
    await database.db.invitations.create_index([("to_email", 1), ("status", 1)])
    await database.db.contributors.create_index([("user_id", 1), ("contributor_id", 1)], unique=True)
    await database.db.stories.create_index([("author_id", 1), ("week_of", 1)])
    await database.db.newspapers.create_index([("user_id", 1), ("week_of", 1)], unique=True)

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()

def get_database():
    return database.db