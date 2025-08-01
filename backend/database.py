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
    # Retry logic for database connection
    import time
    max_retries = 5
    retry_delay = 0.5
    
    for attempt in range(max_retries):
        if database.db is not None:
            return database.db
        
        # If db is None, wait briefly and try again
        print(f"Database not ready, attempt {attempt + 1}/{max_retries}")
        time.sleep(retry_delay)
        
        # Try to reconnect if it's still None
        if database.db is None and attempt < max_retries - 1:
            try:
                import asyncio
                # Create a new event loop if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    # If loop is running, create a task
                    future = asyncio.create_task(connect_to_mongo())
                else:
                    # If loop is not running, run until complete
                    loop.run_until_complete(connect_to_mongo())
            except Exception as e:
                print(f"Reconnection attempt failed: {e}")
    
    if database.db is None:
        print("CRITICAL: Database connection failed after all retries")
    
    return database.db