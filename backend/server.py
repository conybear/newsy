import os
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from contextlib import asynccontextmanager
import base64
from typing import List
from datetime import datetime

from models import *
from database import connect_to_mongo, close_mongo_connection, get_database
from auth import hash_password, verify_password, create_access_token, get_current_user
from utils import get_current_week, is_submission_open, is_published

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Acta Diurna API",
    description="Social newspaper platform where friends share weekly stories",
    version="1.0.0",
    lifespan=lifespan
)

# Production-ready CORS configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Production CORS - allow same origin
    allowed_origins = ["*"]  # Allow all for Docker single-container deployment
else:
    # Development CORS - allow all origins
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/register", response_model=AuthToken)
async def register(user_data: UserCreate):
    """Register a new user"""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        full_name=user_data.full_name
    )
    
    # Hash password and store
    user_dict = user.dict()
    user_dict["password"] = hash_password(user_data.password)
    
    await db.users.insert_one(user_dict)
    
    # Check for pending invitations
    pending_invitations = await db.invitations.find({
        "to_email": user_data.email,
        "status": "pending"
    }).to_list(100)
    
    # Mark invitations as accepted (user can choose to add as contributors later)
    for invitation in pending_invitations:
        await db.invitations.update_one(
            {"id": invitation["id"]},
            {"$set": {"status": "accepted"}}
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return AuthToken(access_token=access_token, user=user)

@app.post("/api/auth/login", response_model=AuthToken)
async def login(credentials: UserLogin):
    """Login user"""
    db = get_database()
    
    # Find user
    user_data = await db.users.find_one({"email": credentials.email})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create user object (without password)
    user = User(**{k: v for k, v in user_data.items() if k != "password"})
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    return AuthToken(access_token=access_token, user=user)

# ===== USER ENDPOINTS =====

@app.get("/api/users/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# ===== INVITATION ENDPOINTS =====

@app.post("/api/invitations/send")
async def send_invitation(invitation_data: dict, current_user: User = Depends(get_current_user)):
    """Send invitation to a friend"""
    db = get_database()
    email = invitation_data.get("email")
    
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Check if already invited
    existing = await db.invitations.find_one({
        "from_user_id": current_user.id,
        "to_email": email,
        "status": {"$in": ["pending", "accepted"]}
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Already invited this email")
    
    # Create invitation
    invitation = Invitation(
        from_user_id=current_user.id,
        from_user_name=current_user.full_name,
        from_user_email=current_user.email,
        to_email=email
    )
    
    await db.invitations.insert_one(invitation.dict())
    
    return {"message": f"Invitation sent to {email}"}

@app.get("/api/invitations/received")
async def get_received_invitations(current_user: User = Depends(get_current_user)):
    """Get invitations received by current user"""
    db = get_database()
    
    invitations = await db.invitations.find({
        "to_email": current_user.email,
        "status": {"$in": ["pending", "accepted"]}
    }).to_list(100)
    
    # Convert MongoDB documents to JSON-serializable format
    for invitation in invitations:
        if "_id" in invitation:
            del invitation["_id"]
    
    return invitations

@app.get("/api/invitations/sent")
async def get_sent_invitations(current_user: User = Depends(get_current_user)):
    """Get invitations sent by current user"""
    db = get_database()
    
    invitations = await db.invitations.find({
        "from_user_id": current_user.id
    }).to_list(100)
    
    # Convert MongoDB documents to JSON-serializable format
    for invitation in invitations:
        if "_id" in invitation:
            del invitation["_id"]
    
    return invitations

# ===== CONTRIBUTOR ENDPOINTS =====

@app.post("/api/contributors/add")
async def add_contributor(data: dict, current_user: User = Depends(get_current_user)):
    """Add bidirectional contributor relationship using atomic updates"""
    db = get_database()
    invitation_id = data.get("invitation_id")
    
    if not invitation_id:
        raise HTTPException(status_code=400, detail="Invitation ID is required")
    
    # Find pending invitation that user can accept
    invitation = await db.invitations.find_one({
        "id": invitation_id,
        "to_email": current_user.email,
        "status": "pending"
    })
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already processed")
    
    # Get the person who invited us
    inviter = await db.users.find_one({"id": invitation["from_user_id"]})
    if not inviter:
        raise HTTPException(status_code=404, detail="Inviter not found")
    
    inviter_id = invitation["from_user_id"]
    current_user_id = current_user.id
    
    # Check if relationship already exists (either direction)
    current_user_doc = await db.users.find_one({"id": current_user_id})
    inviter_doc = await db.users.find_one({"id": inviter_id})
    
    if (current_user_doc and inviter_id in current_user_doc.get("contributors", [])) or \
       (inviter_doc and current_user_id in inviter_doc.get("contributors", [])):
        raise HTTPException(status_code=400, detail="Bidirectional contributor relationship already exists")
    
    # Create bidirectional relationship using atomic updates
    # Update 1: Add inviter as contributor to current user
    result1 = await db.users.update_one(
        {"id": current_user_id},
        {"$addToSet": {"contributors": inviter_id}}
    )
    
    # Update 2: Add current user as contributor to inviter
    result2 = await db.users.update_one(
        {"id": inviter_id},
        {"$addToSet": {"contributors": current_user_id}}
    )
    
    if result1.modified_count == 0 and result2.modified_count == 0:
        raise HTTPException(status_code=400, detail="No changes made - relationship may already exist")
    
    # Mark invitation as accepted
    await db.invitations.update_one(
        {"id": invitation_id},
        {"$set": {"status": "accepted"}}
    )
    
    return {
        "message": f"Created bidirectional contributor relationship with {inviter['full_name']}",
        "relationship": "bidirectional",
        "current_user_updated": result1.modified_count > 0,
        "inviter_updated": result2.modified_count > 0
    }

@app.get("/api/contributors/my")
async def get_my_contributors(current_user: User = Depends(get_current_user)):
    """Get my contributors from User document"""
    db = get_database()
    
    # Get current user document with contributors
    user_doc = await db.users.find_one({"id": current_user.id})
    
    if not user_doc or "contributors" not in user_doc:
        return []
    
    contributor_ids = user_doc["contributors"]
    
    if not contributor_ids:
        return []
    
    # Get contributor user details
    contributors = await db.users.find(
        {"id": {"$in": contributor_ids}},
        {"id": 1, "full_name": 1, "email": 1, "_id": 0}
    ).to_list(100)
    
    # Format for compatibility with existing frontend
    formatted_contributors = []
    for contrib in contributors:
        formatted_contributors.append({
            "contributor_id": contrib["id"],
            "contributor_name": contrib["full_name"],
            "contributor_email": contrib["email"]
        })
    
    return formatted_contributors

@app.delete("/api/contributors/{contributor_id}")
async def remove_contributor(contributor_id: str, current_user: User = Depends(get_current_user)):
    """Remove bidirectional contributor relationship"""
    db = get_database()
    
    # Remove bidirectionally using atomic updates
    # Remove contributor from current user
    result1 = await db.users.update_one(
        {"id": current_user.id},
        {"$pull": {"contributors": contributor_id}}
    )
    
    # Remove current user from contributor
    result2 = await db.users.update_one(
        {"id": contributor_id},
        {"$pull": {"contributors": current_user.id}}
    )
    
    if result1.modified_count == 0 and result2.modified_count == 0:
        raise HTTPException(status_code=404, detail="Contributor relationship not found")
    
    return {"message": "Bidirectional contributor relationship removed"}

# ===== STORY ENDPOINTS =====

@app.post("/api/stories/draft")
async def save_story_draft(draft_data: StoryDraft, current_user: User = Depends(get_current_user)):
    """Save or update story draft"""
    db = get_database()
    current_week = get_current_week()
    
    # Check if draft already exists for this week
    existing_draft = await db.stories.find_one({
        "author_id": current_user.id,
        "week_of": current_week,
        "is_submitted": False
    })
    
    if existing_draft:
        # Update existing draft
        await db.stories.update_one(
            {"id": existing_draft["id"]},
            {"$set": {
                "title": draft_data.title,
                "headline": draft_data.headline,
                "content": draft_data.content,
                "created_at": datetime.utcnow()
            }}
        )
        return {"message": "Draft updated", "id": existing_draft["id"]}
    else:
        # Create new draft
        story = Story(
            author_id=current_user.id,
            author_name=current_user.full_name,
            title=draft_data.title,
            headline=draft_data.headline,
            content=draft_data.content,
            week_of=current_week,
            is_submitted=False
        )
        
        await db.stories.insert_one(story.dict())
        return {"message": "Draft saved", "id": story.id}

@app.get("/api/stories/draft")
async def get_story_draft(current_user: User = Depends(get_current_user)):
    """Get current week's story draft"""
    db = get_database()
    current_week = get_current_week()
    
    draft = await db.stories.find_one({
        "author_id": current_user.id,
        "week_of": current_week,
        "is_submitted": False
    })
    
    if draft:
        # Remove MongoDB ObjectId for JSON serialization
        if "_id" in draft:
            del draft["_id"]
        return draft
    else:
        return {
            "title": "",
            "headline": "",
            "content": "",
            "images": []
        }

@app.get("/api/stories/my")
async def get_my_stories(current_user: User = Depends(get_current_user)):
    """Get all my submitted stories"""
    db = get_database()
    
    stories = await db.stories.find({
        "author_id": current_user.id,
        "is_submitted": True
    }).sort("created_at", -1).to_list(100)
    
    # Clean up ObjectIds
    for story in stories:
        if "_id" in story:
            del story["_id"]
    
    return stories

@app.get("/api/stories/status")
async def get_story_status(current_user: User = Depends(get_current_user)):
    """Get story submission status for current week"""
    db = get_database()
    current_week = get_current_week()
    
    # Check if user has submitted story this week
    submitted_story = await db.stories.find_one({
        "author_id": current_user.id,
        "week_of": current_week,
        "is_submitted": True
    })
    
    # Check if user has draft this week
    draft_story = await db.stories.find_one({
        "author_id": current_user.id,
        "week_of": current_week,
        "is_submitted": False
    })
    
    return {
        "current_week": current_week,
        "has_submitted": submitted_story is not None,
        "has_draft": draft_story is not None,
        "submissions_open": is_submission_open(),
        "deadline": "Monday 11:59 PM EST",
        "story_id": submitted_story["id"] if submitted_story else (draft_story["id"] if draft_story else None)
    }

@app.post("/api/stories/submit")
async def submit_story(story_data: StoryCreate, current_user: User = Depends(get_current_user)):
    """Submit story for publication"""
    db = get_database()
    current_week = get_current_week()
    
    # Check if submissions are open
    if not is_submission_open():
        raise HTTPException(status_code=400, detail="Submissions are closed for this week")
    
    # Check if user already submitted this week
    existing_story = await db.stories.find_one({
        "author_id": current_user.id,
        "week_of": current_week,
        "is_submitted": True
    })
    
    if existing_story:
        raise HTTPException(status_code=400, detail="You have already submitted a story this week")
    
    # Validate required fields
    if not story_data.title.strip() or not story_data.headline.strip() or not story_data.content.strip():
        raise HTTPException(status_code=400, detail="Title, headline, and content are required")
    
    # Check if there's a draft to update
    draft = await db.stories.find_one({
        "author_id": current_user.id,
        "week_of": current_week,
        "is_submitted": False
    })
    
    if draft:
        # Update existing draft and mark as submitted
        await db.stories.update_one(
            {"id": draft["id"]},
            {"$set": {
                "title": story_data.title,
                "headline": story_data.headline,
                "content": story_data.content,
                "is_submitted": True,
                "submitted_at": datetime.utcnow()
            }}
        )
        story_id = draft["id"]
    else:
        # Create new story
        story = Story(
            author_id=current_user.id,
            author_name=current_user.full_name,
            title=story_data.title,
            headline=story_data.headline,
            content=story_data.content,
            week_of=current_week,
            is_submitted=True,
            submitted_at=datetime.utcnow()
        )
        
        await db.stories.insert_one(story.dict())
        story_id = story.id
    
    return {"message": "Story submitted successfully", "id": story_id}

@app.post("/api/stories/{story_id}/images")
async def upload_story_image(
    story_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload image for a story"""
    db = get_database()
    
    # Verify story belongs to user
    story = await db.stories.find_one({
        "id": story_id,
        "author_id": current_user.id
    })
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story["is_submitted"]:
        raise HTTPException(status_code=400, detail="Cannot modify submitted story")
    
    # Check if story already has 3 images
    current_images = story.get("images", [])
    if len(current_images) >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 images per story")
    
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read and encode image
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
    
    # Create image object
    image = StoryImage(
        filename=file.filename,
        content_type=file.content_type,
        data=base64.b64encode(content).decode('utf-8')
    )
    
    # Add image to story
    await db.stories.update_one(
        {"id": story_id},
        {"$push": {"images": image.dict()}}
    )
    
    return {"message": "Image uploaded successfully", "image_id": image.id}

@app.delete("/api/stories/{story_id}/images/{image_id}")
async def delete_story_image(
    story_id: str,
    image_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete image from story"""
    db = get_database()
    
    # Verify story belongs to user
    story = await db.stories.find_one({
        "id": story_id,
        "author_id": current_user.id
    })
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story["is_submitted"]:
        raise HTTPException(status_code=400, detail="Cannot modify submitted story")
    
    # Remove image from story
    await db.stories.update_one(
        {"id": story_id},
        {"$pull": {"images": {"id": image_id}}}
    )
    
    return {"message": "Image deleted successfully"}

@app.get("/api/stories/weekly/{week}")
async def get_weekly_stories(week: str, current_user: User = Depends(get_current_user)):
    """Get all stories for a specific week from user and their contributors"""
    db = get_database()
    
    # Get current user document with contributors
    user_doc = await db.users.find_one({"id": current_user.id})
    
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get contributor IDs from user document  
    contributor_ids = user_doc.get("contributors", [])
    
    # Always include the user's own stories
    all_contributors = contributor_ids + [current_user.id]
    
    # Get all submitted stories from contributors for this week
    stories = await db.stories.find({
        "author_id": {"$in": all_contributors},
        "week_of": week,
        "is_submitted": True
    }).to_list(100)
    
    # Clean up ObjectIds for JSON serialization
    clean_stories = []
    for story in stories:
        if "_id" in story:
            del story["_id"]
        clean_stories.append(story)
    
    return clean_stories

# ===== NEWSPAPER GENERATION ENDPOINTS =====

@app.get("/api/newspapers/current")
async def get_current_newspaper(current_user: User = Depends(get_current_user)):
    """Get current week's newspaper with stories from all contributors"""
    db = get_database()
    current_week = get_current_week()
    
    # Check if newspaper already exists for this week
    existing_newspaper = await db.newspapers.find_one({
        "user_id": current_user.id,
        "week_of": current_week
    })
    
    if existing_newspaper:
        # Clean up ObjectId
        if "_id" in existing_newspaper:
            del existing_newspaper["_id"]
        return existing_newspaper
    
    # Generate new newspaper
    newspaper = await generate_newspaper(current_user.id, current_week)
    return newspaper

@app.get("/api/newspapers/week/{week}")
async def get_newspaper_by_week(week: str, current_user: User = Depends(get_current_user)):
    """Get newspaper for a specific week"""
    db = get_database()
    
    newspaper = await db.newspapers.find_one({
        "user_id": current_user.id,
        "week_of": week
    })
    
    if not newspaper:
        # Generate newspaper for that week
        newspaper = await generate_newspaper(current_user.id, week)
    else:
        # Clean up ObjectId
        if "_id" in newspaper:
            del newspaper["_id"]
    
    return newspaper

@app.get("/api/newspapers/archive")
async def get_newspaper_archive(current_user: User = Depends(get_current_user)):
    """Get list of all published newspapers"""
    db = get_database()
    
    newspapers = await db.newspapers.find({
        "user_id": current_user.id
    }).sort("week_of", -1).to_list(100)
    
    # Clean up ObjectIds and return summary
    archive = []
    for newspaper in newspapers:
        archive.append({
            "week_of": newspaper["week_of"],
            "title": newspaper["title"],
            "published_at": newspaper["published_at"],
            "story_count": len(newspaper.get("stories", [])),
            "contributor_count": len(set(story.get("author_id") for story in newspaper.get("stories", [])))
        })
    
    return archive

@app.post("/api/newspapers/regenerate")
async def regenerate_current_newspaper(current_user: User = Depends(get_current_user)):
    """Force regenerate current week's newspaper"""
    db = get_database()
    current_week = get_current_week()
    
    # Delete existing newspaper
    await db.newspapers.delete_many({
        "user_id": current_user.id,
        "week_of": current_week
    })
    
    # Generate new newspaper
    newspaper = await generate_newspaper(current_user.id, current_week)
    return {"message": "Newspaper regenerated", "newspaper": newspaper}

async def generate_newspaper(user_id: str, week: str) -> dict:
    """Generate newspaper for a user and week using User-based contributors"""
    db = get_database()
    
    # Get user information with contributors
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get contributor IDs from user document
    contributor_ids = user.get("contributors", [])
    
    # Always include the user's own stories
    all_contributors = contributor_ids + [user_id]
    
    # Get all stories from contributors for this week
    stories = await db.stories.find({
        "author_id": {"$in": all_contributors},
        "week_of": week,
        "is_submitted": True
    }).to_list(100)
    
    # If no stories for this week, try to find the most recent week with stories
    if not stories:
        recent_stories = await db.stories.find({
            "author_id": {"$in": all_contributors},
            "is_submitted": True
        }).sort("created_at", -1).to_list(100)
        
        if recent_stories:
            # Group by week and get the most recent week with content
            weeks_with_stories = {}
            for story in recent_stories:
                story_week = story.get("week_of")
                if story_week not in weeks_with_stories:
                    weeks_with_stories[story_week] = []
                weeks_with_stories[story_week].append(story)
            
            # Use stories from the most recent week that has content
            if weeks_with_stories:
                most_recent_week = max(weeks_with_stories.keys())
                stories = weeks_with_stories[most_recent_week]
                week = most_recent_week  # Update week to match content
    
    # Clean up ObjectIds from stories
    clean_stories = []
    for story in stories:
        if "_id" in story:
            del story["_id"]
        clean_stories.append(Story(**story))
    
    # Sort stories: headlines first, then by creation date
    clean_stories.sort(key=lambda s: (not bool(s.headline), s.created_at))
    
    # Create newspaper
    newspaper = Newspaper(
        user_id=user_id,
        week_of=week,
        title=f"Acta Diurna - Week {week}",
        stories=clean_stories,
        published_at=datetime.utcnow()
    )
    
    # Save to database
    await db.newspapers.insert_one(newspaper.dict())
    
    return newspaper.dict()

# ===== HEALTH CHECK =====

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "current_week": get_current_week(),
        "submissions_open": is_submission_open(),
        "published": is_published()
    }