from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import smtplib
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Acta Diurna - Personal Daily Chronicle")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize scheduler
scheduler = AsyncIOScheduler()

# Models
class Story(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    author: str = "Anonymous"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StoryCreate(BaseModel):
    title: str
    content: str
    author: str = "Anonymous"

class Draft(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    author: str = "Anonymous"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DraftCreate(BaseModel):
    title: str
    content: str
    author: str = "Anonymous"

class DraftUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None

class Subscriber(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    subscribed_at: datetime = Field(default_factory=datetime.utcnow)

class SubscriberCreate(BaseModel):
    email: EmailStr

class InviteFriends(BaseModel):
    emails: List[EmailStr]
    message: Optional[str] = "You've been invited to join Acta Diurna!"

class InviteResponse(BaseModel):
    message: str
    sent_count: int

class NewsletterResponse(BaseModel):
    message: str
    story_count: int

# Helper Functions
async def get_weekly_stories():
    """Get stories from the past week"""
    current_time = datetime.utcnow()
    week_ago = current_time - timedelta(days=7)
    
    cursor = db.stories.find({"timestamp": {"$gte": week_ago}})
    stories = await cursor.to_list(1000)
    return [Story(**story) for story in stories]

def compile_newspaper_flipbook(stories: List[Story]) -> str:
    """Generate flipbook-style HTML for weekly chronicle"""
    flipbook_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weekly Chronicle - Acta Diurna</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Georgia', serif;
                background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .flipbook-container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: #92400e;
                color: white;
                text-align: center;
                padding: 30px 20px;
                position: relative;
            }
            .header h1 {
                margin: 0;
                font-size: 2.5em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header .subtitle {
                margin-top: 10px;
                font-size: 1.2em;
                opacity: 0.9;
            }
            .header .date {
                margin-top: 10px;
                font-size: 1.1em;
                opacity: 0.8;
            }
            .flipbook {
                position: relative;
                min-height: 500px;
                padding: 40px;
            }
            .page {
                display: none;
                animation: fadeIn 0.5s ease-in;
            }
            .page.active {
                display: block;
            }
            .page h2 {
                color: #92400e;
                border-bottom: 3px solid #f59e0b;
                padding-bottom: 10px;
                margin-bottom: 20px;
                font-size: 1.8em;
            }
            .page .meta {
                color: #7f8c8d;
                font-style: italic;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .page .author {
                background: #fef3c7;
                color: #92400e;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 500;
            }
            .page .content {
                line-height: 1.8;
                font-size: 1.1em;
                text-align: justify;
                margin-bottom: 30px;
                color: #374151;
            }
            .page .content strong {
                font-weight: bold;
            }
            .page .content em {
                font-style: italic;
            }
            .page .content u {
                text-decoration: underline;
            }
            .navigation {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 40px;
                background: #fef3c7;
                border-top: 1px solid #f59e0b;
            }
            .nav-btn {
                background: #f59e0b;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 1em;
                transition: all 0.3s ease;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                font-weight: 600;
            }
            .nav-btn:hover:not(:disabled) {
                background: #d97706;
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.3);
            }
            .nav-btn:disabled {
                background: #bdc3c7;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .page-indicator {
                background: #92400e;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
            }
            .no-stories {
                text-align: center;
                padding: 60px 20px;
                color: #7f8c8d;
            }
            .no-stories h3 {
                font-size: 1.5em;
                margin-bottom: 10px;
                color: #92400e;
            }
            .friends-badge {
                display: inline-block;
                background: #fef3c7;
                color: #92400e;
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 0.8em;
                margin-top: 10px;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @media (max-width: 768px) {
                .flipbook-container {
                    margin: 10px;
                    border-radius: 10px;
                }
                .flipbook {
                    padding: 20px;
                }
                .navigation {
                    padding: 15px 20px;
                }
                .header h1 {
                    font-size: 2em;
                }
                .page .meta {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }
            }
        </style>
    </head>
    <body>
        <div class="flipbook-container">
            <div class="header">
                <h1>📜 Acta Diurna</h1>
                <div class="subtitle">Weekly Chronicle</div>
                <div class="date">""" + datetime.now().strftime("%B %d, %Y") + """</div>
                <div class="friends-badge">Stories from Friends</div>
            </div>
            <div class="flipbook">
    """

    if not stories:
        flipbook_html += '''
            <div class="page active no-stories">
                <h3>No stories this week from your circle</h3>
                <p>Encourage your friends to share their experiences and thoughts!</p>
                <p style="color: #92400e; font-weight: 500;">Remember: Only invited friends can share stories in your Acta Diurna.</p>
            </div>
        '''
    else:
        for i, story in enumerate(stories):
            active_class = "active" if i == 0 else ""
            flipbook_html += f'''
            <div class="page {active_class}">
                <h2>{story.title}</h2>
                <div class="meta">
                    <div class="author">📝 {story.author}</div>
                    <span><strong>Shared:</strong> {story.timestamp.strftime("%B %d, %Y at %I:%M %p")}</span>
                </div>
                <div class="content">
                    {story.content}
                </div>
            </div>
            '''

    flipbook_html += f'''
            </div>
            <div class="navigation">
                <button class="nav-btn" id="prevBtn" onclick="prevPage()">← Previous</button>
                <div class="page-indicator">
                    <span id="currentPage">1</span> / <span id="totalPages">{max(1, len(stories))}</span>
                </div>
                <button class="nav-btn" id="nextBtn" onclick="nextPage()">Next →</button>
            </div>
        </div>

        <script>
            let currentPage = 0;
            const totalPages = {len(stories) if stories else 1};
            
            function showPage(idx) {{
                const pages = document.querySelectorAll('.page');
                pages.forEach((p, i) => {{
                    p.classList.toggle('active', i === idx);
                }});
                
                document.getElementById('currentPage').textContent = idx + 1;
                document.getElementById('prevBtn').disabled = idx === 0;
                document.getElementById('nextBtn').disabled = idx === totalPages - 1;
            }}
            
            function prevPage() {{
                if (currentPage > 0) {{
                    currentPage--;
                    showPage(currentPage);
                }}
            }}
            
            function nextPage() {{
                if (currentPage < totalPages - 1) {{
                    currentPage++;
                    showPage(currentPage);
                }}
            }}
            
            // Keyboard navigation
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'ArrowLeft') prevPage();
                if (e.key === 'ArrowRight') nextPage();
            }});
            
            // Initialize
            window.onload = function() {{
                showPage(0);
            }};
        </script>
    </body>
    </html>
    '''
    return flipbook_html

async def send_friend_invitations(emails: List[str], custom_message: str = ""):
    """Send invitation emails to friends"""
    try:
        # Email configuration
        sender_email = os.environ.get('NEWSLETTER_EMAIL', 'your_email@example.com')
        sender_password = os.environ.get('NEWSLETTER_PASSWORD', 'your_email_password')
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        
        sent_count = 0
        
        for email in emails:
            try:
                message = MIMEMultipart("alternative")
                message["Subject"] = "You're Invited to Join Acta Diurna - Your Friends' Chronicle!"
                message["From"] = sender_email
                message["To"] = email
                
                # Create invitation HTML
                invitation_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Georgia, serif; line-height: 1.6; color: #374151; }}
                        .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                        .header {{ background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%); color: white; padding: 30px; text-align: center; }}
                        .content {{ padding: 30px; }}
                        .button {{ background: #f59e0b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; display: inline-block; font-weight: bold; }}
                        .footer {{ background: #fef3c7; padding: 20px; text-align: center; color: #92400e; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>📜 Acta Diurna</h1>
                            <p>You've been invited to join a private chronicle!</p>
                        </div>
                        <div class="content">
                            <h2>Welcome to Your Circle of Friends</h2>
                            <p>A friend has invited you to join their Acta Diurna - a private daily chronicle where close friends share stories, experiences, and thoughts.</p>
                            
                            <h3>What is Acta Diurna?</h3>
                            <ul>
                                <li>📝 Share personal stories and experiences with trusted friends</li>
                                <li>📖 Read stories from your circle in an interactive flipbook format</li>
                                <li>📧 Receive weekly chronicles with all your friends' stories</li>
                                <li>👥 Private and secure - only invited friends can participate</li>
                            </ul>
                            
                            {f'<p><strong>Personal message:</strong> {custom_message}</p>' if custom_message else ''}
                            
                            <p style="text-align: center; margin: 30px 0;">
                                <a href="https://dddc6d0c-9b98-4632-81b7-760632b6b5b6.preview.emergentagent.com" class="button">
                                    Join Your Circle
                                </a>
                            </p>
                            
                            <p><em>Start sharing your stories and stay connected with your friends in a meaningful way.</em></p>
                        </div>
                        <div class="footer">
                            <p>Acta Diurna - Where Friends Share Stories</p>
                            <p style="font-size: 0.9em;">This is a private invitation. Only invited members can access your circle.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                message.attach(MIMEText(invitation_html, "html"))
                
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, email, message.as_string())
                    
                sent_count += 1
                logging.info(f"Invitation sent to {email}")
                
            except Exception as e:
                logging.error(f"Failed to send invitation to {email}: {str(e)}")
                
        return sent_count
        
    except Exception as e:
        logging.error(f"Invitation sending failed: {str(e)}")
        return 0

async def send_newsletter():
    """Send weekly chronicle to all subscribers"""
    try:
        # Get weekly stories
        weekly_stories = await get_weekly_stories()
        
        # Get all subscribers
        cursor = db.subscribers.find({})
        subscribers = await cursor.to_list(1000)
        
        if not subscribers:
            logging.info("No subscribers found for chronicle")
            return
        
        # Generate chronicle content
        newsletter_content = compile_newspaper_flipbook(weekly_stories)
        
        # Email configuration
        sender_email = os.environ.get('NEWSLETTER_EMAIL', 'your_email@example.com')
        sender_password = os.environ.get('NEWSLETTER_PASSWORD', 'your_email_password')
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        
        # Send emails
        for subscriber in subscribers:
            try:
                message = MIMEMultipart("alternative")
                message["Subject"] = "Your Weekly Chronicle - Stories from Friends"
                message["From"] = sender_email
                message["To"] = subscriber['email']
                
                message.attach(MIMEText(newsletter_content, "html"))
                
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, subscriber['email'], message.as_string())
                    
                logging.info(f"Chronicle sent to {subscriber['email']}")
                
            except Exception as e:
                logging.error(f"Failed to send chronicle to {subscriber['email']}: {str(e)}")
                
    except Exception as e:
        logging.error(f"Chronicle sending failed: {str(e)}")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Welcome to Acta Diurna - Your Personal Daily Chronicle"}

@api_router.post("/stories", response_model=Story)
async def create_story(story_input: StoryCreate):
    """Share a new story with friends"""
    story_dict = story_input.dict()
    story = Story(**story_dict)
    
    await db.stories.insert_one(story.dict())
    return story

@api_router.get("/stories", response_model=List[Story])
async def get_stories(limit: int = 50, skip: int = 0):
    """Get all stories from friends with pagination"""
    cursor = db.stories.find().sort("timestamp", -1).skip(skip).limit(limit)
    stories = await cursor.to_list(limit)
    return [Story(**story) for story in stories]

@api_router.get("/stories/weekly", response_model=List[Story])
async def get_weekly_stories_endpoint():
    """Get stories from friends from the past week"""
    return await get_weekly_stories()

# Draft endpoints
@api_router.post("/drafts", response_model=Draft)
async def create_draft(draft_input: DraftCreate):
    """Save a story draft"""
    draft_dict = draft_input.dict()
    draft = Draft(**draft_dict)
    
    await db.drafts.insert_one(draft.dict())
    return draft

@api_router.get("/drafts", response_model=List[Draft])
async def get_drafts():
    """Get all saved drafts"""
    cursor = db.drafts.find().sort("updated_at", -1)
    drafts = await cursor.to_list(1000)
    return [Draft(**draft) for draft in drafts]

@api_router.put("/drafts/{draft_id}", response_model=Draft)
async def update_draft(draft_id: str, draft_update: DraftUpdate):
    """Update a saved draft"""
    update_data = {k: v for k, v in draft_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.drafts.update_one(
        {"id": draft_id}, 
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    updated_draft = await db.drafts.find_one({"id": draft_id})
    return Draft(**updated_draft)

@api_router.delete("/drafts/{draft_id}")
async def delete_draft(draft_id: str):
    """Delete a saved draft"""
    result = await db.drafts.delete_one({"id": draft_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Draft not found")
    return {"message": "Draft deleted successfully"}

@api_router.get("/newspaper/flipbook")
async def get_flipbook_newspaper():
    """Get the flipbook version of weekly chronicle"""
    from starlette.responses import HTMLResponse
    weekly_stories = await get_weekly_stories()
    flipbook_html = compile_newspaper_flipbook(weekly_stories)
    return HTMLResponse(content=flipbook_html)

@api_router.post("/invite-friends", response_model=InviteResponse)
async def invite_friends(invite_data: InviteFriends):
    """Send invitations to friends to join your circle"""
    if len(invite_data.emails) > 50:
        raise HTTPException(status_code=400, detail="Cannot invite more than 50 friends at once")
    
    sent_count = await send_friend_invitations(
        [email.lower() for email in invite_data.emails],
        invite_data.message
    )
    
    return InviteResponse(
        message=f"Successfully sent {sent_count} invitation(s)",
        sent_count=sent_count
    )

@api_router.post("/subscribe", response_model=Subscriber)
async def subscribe_to_chronicle(subscriber_input: SubscriberCreate):
    """Subscribe to weekly chronicle"""
    # Check if email already exists
    existing = await db.subscribers.find_one({"email": subscriber_input.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    
    subscriber = Subscriber(email=subscriber_input.email)
    await db.subscribers.insert_one(subscriber.dict())
    return subscriber

@api_router.delete("/unsubscribe/{email}")
async def unsubscribe_from_chronicle(email: str):
    """Unsubscribe from chronicle"""
    result = await db.subscribers.delete_one({"email": email})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Successfully unsubscribed"}

@api_router.get("/subscribers")
async def get_subscribers():
    """Get all subscribers (admin only)"""
    cursor = db.subscribers.find({})
    subscribers = await cursor.to_list(1000)
    return {"count": len(subscribers), "subscribers": [Subscriber(**sub) for sub in subscribers]}

@api_router.post("/newsletter/send")
async def send_newsletter_manually():
    """Manually trigger chronicle sending"""
    await send_newsletter()
    weekly_stories = await get_weekly_stories()
    return NewsletterResponse(
        message="Chronicle sent successfully",
        story_count=len(weekly_stories)
    )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    # Schedule weekly chronicle (every Monday at 9 AM)
    scheduler.add_job(
        send_newsletter,
        'cron',
        day_of_week='mon',
        hour=9,
        minute=0
    )
    scheduler.start()
    logger.info("Chronicle scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    client.close()
    logger.info("Application shutdown complete")