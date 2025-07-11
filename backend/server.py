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

@app.post("/api/friends/request")
async def send_friend_request(request: FriendRequest, current_user: User = Depends(get_current_user)):
    """Send a friend request"""
    # Find the user to befriend
    friend = await db.users.find_one({"email": request.email})
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    friend_user = User(**friend)
    
    # Check if already friends
    if friend_user.id in current_user.friends:
        raise HTTPException(status_code=400, detail="Already friends")
    
    # Check friend limit (50)
    if len(current_user.friends) >= 50:
        raise HTTPException(status_code=400, detail="Friend limit reached (50)")
    
    # Add to friends list (both ways)
    await db.users.update_one(
        {"id": current_user.id},
        {"$addToSet": {"friends": friend_user.id}}
    )
    await db.users.update_one(
        {"id": friend_user.id},
        {"$addToSet": {"friends": current_user.id}}
    )
    
    return {"message": "Friend request sent successfully"}

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
    
    # Check if edition already exists
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
