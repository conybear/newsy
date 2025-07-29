from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

async def fix_all_contributors():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    users = await db.users.find({}).to_list(1000)
    print(f"Found {len(users)} users.")

    for user in users:
        user_id = user['id']
        user_email = user['email']
        friends = user.get('friends', [])
        
        # Set contributors = friends (remove duplicates, just in case)
        contributors = list(set(friends))

        # Update this user
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"contributors": contributors}}
        )

        # For each friend, add this user as contributor to their record
        for friend_id in friends:
            await db.users.update_one(
                {"id": friend_id},
                {"$addToSet": {"contributors": user_id}}
            )

        print(f"Updated user {user_email} ({user_id}): contributors set to {contributors}")

    print("Contributor migration complete.")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_all_contributors())