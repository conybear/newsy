from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

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
    is_active: bool = True

class Invitation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str
    from_user_name: str
    from_user_email: EmailStr
    to_email: EmailStr
    status: str = "pending"  # pending, accepted, declined
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Contributor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Who has this contributor
    contributor_id: str  # Who is the contributor
    contributor_name: str
    contributor_email: EmailStr
    added_at: datetime = Field(default_factory=datetime.utcnow)

class StoryImage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content_type: str
    data: str  # base64 encoded

class Story(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    author_name: str
    title: str
    headline: str
    content: str
    images: List[StoryImage] = Field(default_factory=list)
    week_of: str  # Format: "2024-W52"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_submitted: bool = False
    submitted_at: Optional[datetime] = None

class StoryCreate(BaseModel):
    title: str
    headline: str
    content: str

class StoryDraft(BaseModel):
    title: str = ""
    headline: str = ""
    content: str = ""

class Newspaper(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    week_of: str
    title: str = "Acta Diurna"
    stories: List[Story] = Field(default_factory=list)
    published_at: datetime = Field(default_factory=datetime.utcnow)

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User