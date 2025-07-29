from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import os
import logging
import uuid
import bcrypt
import base64
from jose import JWTError, jwt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Environment variables
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
jwt_secret = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
jwt_algorithm = "HS256"
jwt_expiration_hours = 24

# MongoDB connection
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# FastAPI app
app = FastAPI(title="Social Weekly Newspaper API")

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== MODELS =====

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    friends: List[str] = Field(default_factory=list)  # List of user IDs
    contributors: List[str] = Field(default_factory=list)  # List of user IDs
    is_active: bool = True

class StoryImage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content_type: str
    data: str  # base64 encoded image data

class Story(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    author_id: str
    author_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    images: List[StoryImage] = Field(default_factory=list)
    is_headline: bool = False
    week_of: str  # Format: "2024-W01" (ISO week)

class StoryCreate(BaseModel):
    title: str
    content: str
    is_headline: bool = False

class WeeklyEdition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    week_of: str  # Format: "2024-W01" (ISO week)
    stories: List[Story] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FriendRequest(BaseModel):
    email: EmailStr

class Invitation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str
    from_user_name: str
    to_email: EmailStr
    status: str = "pending"  # pending, accepted, expired
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=30))

class InvitationCreate(BaseModel):
    email: EmailStr

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ===== UTILITY FUNCTIONS =====

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=jwt_expiration_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_secret, algorithm=jwt_algorithm)
    return encoded_jwt

def get_current_week() -> str:
    """Get current week in ISO format (YYYY-WXX)"""
    return datetime.now().strftime("%Y-W%U")

def get_week_start_date(week_str: str) -> datetime:
    """Convert week string to start date"""
    try:
        year, week = week_str.split('-W')
        # Calculate the start of the week (Tuesday)
        jan1 = datetime(int(year), 1, 1)
        week_start = jan1 + timedelta(weeks=int(week))
        # Adjust to Tuesday
        days_to_tuesday = (1 - week_start.weekday()) % 7
        return week_start + timedelta(days=days_to_tuesday)
    except:
        return datetime.utcnow()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, jwt_secret, algorithms=[jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/register", response_model=AuthToken)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name
    )
    
    # Store user with hashed password
    user_dict = user.dict()
    user_dict['password'] = hashed_password
    await db.users.insert_one(user_dict)
    
    # Check for pending invitations and auto-accept them
    pending_invitations = await db.invitations.find({
        "to_email": user_data.email,
        "status": "pending"
    }).to_list(100)
    
    for invitation in pending_invitations:
        # Add both users as friends and contributors
        await db.users.update_one(
            {"id": user.id},
            {"$addToSet": {"friends": invitation["from_user_id"], "contributors": invitation["from_user_id"]}}
        )
        await db.users.update_one(
            {"id": invitation["from_user_id"]},
            {"$addToSet": {"friends": user.id, "contributors": user.id}}
        )
        
        # Mark invitation as accepted
        await db.invitations.update_one(
            {"id": invitation["id"]},
            {"$set": {"status": "accepted"}}
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return AuthToken(access_token=access_token)

@app.post("/api/auth/login", response_model=AuthToken)
async def login(user_credentials: UserLogin):
    """Login user"""
    # Find user
    user = await db.users.find_one({"email": user_credentials.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(user_credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user['email']})
    return AuthToken(access_token=access_token)

# ===== USER ENDPOINTS =====

@app.get("/api/users/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/api/users/search")
async def search_users(email: str, current_user: User = Depends(get_current_user)):
    """Search users by email"""
    user = await db.users.find_one({"email": email}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# ===== FRIEND MANAGEMENT ENDPOINTS =====

@app.post("/api/friends/invite")
async def send_friend_invitation(request: InvitationCreate, current_user: User = Depends(get_current_user)):
    """Send a friend invitation"""
    # Check friend limit (50)
    if len(current_user.friends) >= 50:
        raise HTTPException(status_code=400, detail="Friend limit reached (50)")
    
    # Check if user is trying to invite themselves
    if request.email == current_user.email:
        raise HTTPException(status_code=400, detail="Cannot invite yourself")
    
    # Check if the email belongs to an existing user
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        existing_user_obj = User(**existing_user)
        # Check if already friends
        if existing_user_obj.id in current_user.friends:
            raise HTTPException(status_code=400, detail="Already friends with this user")
        
        # If user exists, add as friend immediately
        await db.users.update_one(
            {"id": current_user.id},
            {"$addToSet": {"friends": existing_user_obj.id, "contributors": existing_user_obj.id}}
        )
        await db.users.update_one(
            {"id": existing_user_obj.id},
            {"$addToSet": {"friends": current_user.id, "contributors": current_user.id}}
        )
        
        return {"message": f"Successfully added {existing_user_obj.full_name} as a friend!"}
    
    # Check if invitation already exists
    existing_invitation = await db.invitations.find_one({
        "from_user_id": current_user.id,
        "to_email": request.email,
        "status": "pending"
    })
    if existing_invitation:
        raise HTTPException(status_code=400, detail="Invitation already sent to this email")
    
    # Create invitation
    invitation = Invitation(
        from_user_id=current_user.id,
        from_user_name=current_user.full_name,
        to_email=request.email
    )
    
    # Store invitation
    await db.invitations.insert_one(invitation.dict())
    
    return {
        "message": f"Invitation sent to {request.email}! They will be added as a friend when they join Weekly Chronicles.",
        "invitation_id": invitation.id
    }

@app.get("/api/friends/invitations")
async def get_pending_invitations(current_user: User = Depends(get_current_user)):
    """Get pending invitations sent by current user"""
    invitations = await db.invitations.find({
        "from_user_id": current_user.id,
        "status": "pending"
    }).to_list(100)
    
    return [Invitation(**invitation) for invitation in invitations]

@app.delete("/api/friends/invitations/{invitation_id}")
async def cancel_invitation(invitation_id: str, current_user: User = Depends(get_current_user)):
    """Cancel a pending invitation"""
    invitation = await db.invitations.find_one({
        "id": invitation_id,
        "from_user_id": current_user.id,
        "status": "pending"
    })
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    await db.invitations.update_one(
        {"id": invitation_id},
        {"$set": {"status": "cancelled"}}
    )
    
    return {"message": "Invitation cancelled successfully"}

@app.get("/api/friends", response_model=List[User])
async def get_friends(current_user: User = Depends(get_current_user)):
    """Get user's friends list"""
    friends = await db.users.find(
        {"id": {"$in": current_user.friends}},
        {"password": 0}
    ).to_list(100)
    return [User(**friend) for friend in friends]

@app.post("/api/friends/contributors")
async def set_contributors(contributor_ids: List[str], current_user: User = Depends(get_current_user)):
    """Set which friends are contributors to weekly edition"""
    # Validate all IDs are friends
    if not all(friend_id in current_user.friends for friend_id in contributor_ids):
        raise HTTPException(status_code=400, detail="All contributors must be friends")
    
    # Update contributors
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"contributors": contributor_ids}}
    )
    
    return {"message": "Contributors updated successfully"}

# ===== STORY ENDPOINTS =====

@app.post("/api/stories", response_model=Story)
async def create_story(story_data: StoryCreate, current_user: User = Depends(get_current_user)):
    """Create a new story"""
    current_week = get_current_week()
    
    # Check if user already submitted a story this week
    existing_story = await db.stories.find_one({
        "author_id": current_user.id,
        "week_of": current_week
    })
    if existing_story:
        raise HTTPException(status_code=400, detail="You already submitted a story this week")
    
    # Create story
    story = Story(
        title=story_data.title,
        content=story_data.content,
        author_id=current_user.id,
        author_name=current_user.full_name,
        is_headline=story_data.is_headline,
        week_of=current_week
    )
    
    # Store story
    await db.stories.insert_one(story.dict())
    return story

@app.post("/api/stories/{story_id}/images")
async def upload_story_image(story_id: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Upload an image for a story"""
    # Find story
    story = await db.stories.find_one({"id": story_id, "author_id": current_user.id})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Check if story already has 3 images
    if len(story.get('images', [])) >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 images per story")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read and encode image
    image_data = await file.read()
    encoded_image = base64.b64encode(image_data).decode('utf-8')
    
    # Create image object
    image = StoryImage(
        filename=file.filename,
        content_type=file.content_type,
        data=encoded_image
    )
    
    # Add image to story
    await db.stories.update_one(
        {"id": story_id},
        {"$push": {"images": image.dict()}}
    )
    
    return {"message": "Image uploaded successfully", "image_id": image.id}

@app.get("/api/stories/my", response_model=List[Story])
async def get_my_stories(current_user: User = Depends(get_current_user)):
    """Get current user's stories"""
    stories = await db.stories.find({"author_id": current_user.id}).to_list(100)
    return [Story(**story) for story in stories]

@app.get("/api/stories/weekly/{week}")
async def get_weekly_stories(week: str, current_user: User = Depends(get_current_user)):
    """Get stories for a specific week"""
    # Get stories from user's contributors
    user_data = await db.users.find_one({"id": current_user.id})
    contributors = user_data.get('contributors', [])
    
    # Include current user's story
    all_contributors = contributors + [current_user.id]
    
    stories = await db.stories.find({
        "author_id": {"$in": all_contributors},
        "week_of": week
    }).to_list(100)
    
    return [Story(**story) for story in stories]

# ===== WEEKLY EDITION ENDPOINTS =====

@app.get("/api/editions/current")
async def get_current_edition(current_user: User = Depends(get_current_user)):
    """Get current week's edition"""
    current_week = get_current_week()
    
    # Check if edition already exists for current week
    existing_edition = await db.weekly_editions.find_one({
        "user_id": current_user.id,
        "week_of": current_week
    })
    
    if existing_edition:
        return WeeklyEdition(**existing_edition)
    
    # Generate new edition
    user_data = await db.users.find_one({"id": current_user.id})
    contributors = user_data.get('contributors', [])
    all_contributors = contributors + [current_user.id]
    
    # Get stories for this week
    stories = await db.stories.find({
        "author_id": {"$in": all_contributors},
        "week_of": current_week
    }).to_list(100)
    
    # If no stories for current week, get the most recent week with stories
    if not stories:
        # Find the most recent week that has stories from contributors
        recent_stories = await db.stories.find({
            "author_id": {"$in": all_contributors}
        }).sort("created_at", -1).limit(100).to_list(100)
        
        if recent_stories:
            # Group by week and get the most recent week with content
            weeks_with_stories = {}
            for story in recent_stories:
                week = story.get("week_of")
                if week not in weeks_with_stories:
                    weeks_with_stories[week] = []
                weeks_with_stories[week].append(story)
            
            # Get the most recent week
            if weeks_with_stories:
                most_recent_week = max(weeks_with_stories.keys())
                stories = recent_stories
                current_week = most_recent_week  # Use the week that actually has content
    
    # Create edition
    edition = WeeklyEdition(
        user_id=current_user.id,
        week_of=current_week,
        stories=[Story(**story) for story in stories]
    )
    
    # Store edition
    await db.weekly_editions.insert_one(edition.dict())
    
    return edition

@app.get("/api/editions/archive")
async def get_edition_archive(current_user: User = Depends(get_current_user)):
    """Get archive of past editions"""
    editions = await db.weekly_editions.find({
        "user_id": current_user.id
    }).sort("week_of", -1).to_list(100)
    
    return [WeeklyEdition(**edition) for edition in editions]

@app.get("/api/editions/{week}")
async def get_edition_by_week(week: str, current_user: User = Depends(get_current_user)):
    """Get edition for specific week"""
    edition = await db.weekly_editions.find_one({
        "user_id": current_user.id,
        "week_of": week
    })
    
    if not edition:
        raise HTTPException(status_code=404, detail="Edition not found")
    
    return WeeklyEdition(**edition)

@app.get("/api/debug/edition-logic")
async def debug_edition_logic(current_user: User = Depends(get_current_user)):
    """Debug the weekly edition generation logic"""
    current_week = get_current_week()
    
    # Get user data
    user_data = await db.users.find_one({"id": current_user.id})
    contributors = user_data.get('contributors', [])
    all_contributors = contributors + [current_user.id]
    
    # Check for existing edition
    existing_edition = await db.weekly_editions.find_one({
        "user_id": current_user.id,
        "week_of": current_week
    })
    
    # Get all stories from contributors for current week
    current_week_stories = await db.stories.find({
        "author_id": {"$in": all_contributors},
        "week_of": current_week
    }).to_list(100)
    
    # Get all stories from contributors (any week)
    all_stories = await db.stories.find({
        "author_id": {"$in": all_contributors}
    }).to_list(100)
    
    return {
        "current_week": current_week,
        "user_id": current_user.id,
        "contributors": contributors,
        "all_contributors": all_contributors,
        "existing_edition_exists": existing_edition is not None,
        "existing_edition_story_count": len(existing_edition.get("stories", [])) if existing_edition else 0,
        "current_week_stories_found": len(current_week_stories),
        "current_week_stories": [
            {
                "title": s.get("title"),
                "author_name": s.get("author_name"), 
                "author_id": s.get("author_id"),
                "week_of": s.get("week_of")
            } for s in current_week_stories
        ],
        "total_stories_from_contributors": len(all_stories),
        "all_stories": [
            {
                "title": s.get("title"),
                "author_name": s.get("author_name"),
                "author_id": s.get("author_id"), 
                "week_of": s.get("week_of")
            } for s in all_stories
        ]
    }

@app.post("/api/admin/fix-contributors")
async def fix_contributors_migration(current_user: User = Depends(get_current_user)):
    """One-time migration to fix friend/contributor relationships"""
    try:
        # Get current user's friends
        user_data = await db.users.find_one({"id": current_user.id})
        friends_list = user_data.get('friends', [])
        
        if friends_list:
            # Add all friends as contributors
            await db.users.update_one(
                {"id": current_user.id},
                {"$addToSet": {"contributors": {"$each": friends_list}}}
            )
            
            # Also add current user as contributor to all friends
            for friend_id in friends_list:
                await db.users.update_one(
                    {"id": friend_id},
                    {"$addToSet": {"contributors": current_user.id}}
                )
            
            return {
                "message": f"Successfully fixed contributors! Added {len(friends_list)} friends as contributors.",
                "friends_added": len(friends_list)
            }
        else:
            return {"message": "No friends found to add as contributors"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.get("/api/debug/user-info")
async def debug_user_info(current_user: User = Depends(get_current_user)):
    """Debug endpoint to see complete user info and relationships"""
    # Get full user data from database
    user_data = await db.users.find_one({"id": current_user.id})
    
    # Get friends data
    friends_data = []
    if user_data.get('friends'):
        friends = await db.users.find(
            {"id": {"$in": user_data['friends']}},
            {"password": 0}
        ).to_list(100)
        friends_data = friends
    
    # Get stories from all contributors
    contributors = user_data.get('contributors', []) + [current_user.id]
    contributor_stories = await db.stories.find({
        "author_id": {"$in": contributors}
    }).to_list(100)
    
    # Get current week
    current_week = get_current_week()
    
    return {
        "user": user_data,
        "friends_data": friends_data,
        "contributors": contributors,
        "contributor_stories": contributor_stories,
        "current_week": current_week,
        "diagnosis": {
            "has_friends": len(user_data.get('friends', [])) > 0,
            "has_contributors": len(user_data.get('contributors', [])) > 0,
            "friends_count": len(user_data.get('friends', [])),
            "contributors_count": len(user_data.get('contributors', [])),
            "contributor_stories_count": len(contributor_stories),
            "problem": "No contributors" if len(user_data.get('contributors', [])) == 0 else None
        }
    }

# ===== HEALTH CHECK =====

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
