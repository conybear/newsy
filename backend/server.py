from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
        "status": "accepted"
    }).to_list(100)
    
    return invitations

@app.get("/api/invitations/sent")
async def get_sent_invitations(current_user: User = Depends(get_current_user)):
    """Get invitations sent by current user"""
    db = get_database()
    
    invitations = await db.invitations.find({
        "from_user_id": current_user.id
    }).to_list(100)
    
    return invitations

# ===== CONTRIBUTOR ENDPOINTS =====

@app.post("/api/contributors/add")
async def add_contributor(data: dict, current_user: User = Depends(get_current_user)):
    """Add someone as a contributor (from accepted invitations)"""
    db = get_database()
    invitation_id = data.get("invitation_id")
    
    if not invitation_id:
        raise HTTPException(status_code=400, detail="Invitation ID is required")
    
    # Find accepted invitation
    invitation = await db.invitations.find_one({
        "id": invitation_id,
        "to_email": current_user.email,
        "status": "accepted"
    })
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")
    
    # Get the person who invited us
    inviter = await db.users.find_one({"id": invitation["from_user_id"]})
    if not inviter:
        raise HTTPException(status_code=404, detail="Inviter not found")
    
    # Check if already a contributor
    existing = await db.contributors.find_one({
        "user_id": current_user.id,
        "contributor_id": invitation["from_user_id"]
    })
    
    if existing:
        raise HTTPException(status_code=400, detail="Already added as contributor")
    
    # Add as contributor
    contributor = Contributor(
        user_id=current_user.id,
        contributor_id=invitation["from_user_id"],
        contributor_name=inviter["full_name"],
        contributor_email=inviter["email"]
    )
    
    await db.contributors.insert_one(contributor.dict())
    
    return {"message": f"Added {inviter['full_name']} as contributor"}

@app.get("/api/contributors/my")
async def get_my_contributors(current_user: User = Depends(get_current_user)):
    """Get my contributors"""
    db = get_database()
    
    contributors = await db.contributors.find({
        "user_id": current_user.id
    }).to_list(100)
    
    return contributors

@app.delete("/api/contributors/{contributor_id}")
async def remove_contributor(contributor_id: str, current_user: User = Depends(get_current_user)):
    """Remove a contributor"""
    db = get_database()
    
    result = await db.contributors.delete_one({
        "user_id": current_user.id,
        "contributor_id": contributor_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contributor not found")
    
    return {"message": "Contributor removed"}

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