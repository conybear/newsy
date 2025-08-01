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
    
    # Test the connection
    try:
        await database.db.command("ismaster")
        print(f"Connected to MongoDB at {MONGO_URL}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return
    
    # Create indexes for better performance (with error handling)
    try:
        await database.db.users.create_index("email", unique=True)
    except Exception as e:
        print(f"Could not create users.email index: {e}")
    
    try:
        await database.db.invitations.create_index([("to_email", 1), ("status", 1)])
    except Exception as e:
        print(f"Could not create invitations index: {e}")
    
    try:
        await database.db.contributors.create_index([("user_id", 1), ("contributor_id", 1)], unique=True)
    except Exception as e:
        print(f"Could not create contributors index: {e}")
    
    try:
        await database.db.stories.create_index([("author_id", 1), ("week_of", 1)])
    except Exception as e:
        print(f"Could not create stories index: {e}")
    
    try:
        await database.db.newspapers.create_index([("user_id", 1), ("week_of", 1)], unique=True)
    except Exception as e:
        print(f"Could not create newspapers index: {e}")

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()

def get_database():
    if database.db is None:
        # If db is None, try to reconnect
        import asyncio
        try:
            asyncio.create_task(connect_to_mongo())
        except:
            pass
    return database.db