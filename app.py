import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging

app = Flask(__name__)

# Setup logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Log startup information
logger.info("🎉 Acta Diurna Flask application starting...")
logger.info(f"🌐 Environment: {'Production' if os.environ.get('PORT') else 'Development'}")

# Verify build directory exists
build_dir = os.path.join(os.path.dirname(__file__), 'build')
if os.path.exists(build_dir):
    logger.info("✅ Build directory found - deployment assets ready")
else:
    logger.warning("⚠️ Build directory not found - this may cause deployment issues")

# In-memory storage for stories and subscribers
stories = []
subscribers = []

# Load sensitive data from environment variables
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

# Log email configuration status
if SENDER_EMAIL and SENDER_PASSWORD:
    logger.info("📧 Email configuration: ENABLED")
else:
    logger.info("📧 Email configuration: DISABLED (environment variables not set)")

# Helper function to compile a weekly newspaper
def compile_newspaper():
    current_time = datetime.now()
    week_ago = current_time - timedelta(days=7)
    weekly_stories = [story for story in stories if story['timestamp'] >= week_ago]

    newspaper_content = "<h1>Weekly Newspaper</h1>"
    newspaper_content += "<p>Here are the stories from the past week:</p><ul>"
    for story in weekly_stories:
        newspaper_content += f"<li><h3>{story['title']}</h3><p><strong>Author:</strong> {story['author']}</p><p>{story['content']}</p></li>"
    newspaper_content += "</ul>"

    return newspaper_content

# Helper function to send the newspaper via email
def send_newspaper():
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        logger.error("SENDER_EMAIL and SENDER_PASSWORD must be set as environment variables.")
        return

    newspaper_content = compile_newspaper()
    for subscriber in subscribers:
        recipient_email = subscriber['email']
        message = MIMEMultipart("alternative")
        message["Subject"] = "Weekly Newspaper"
        message["From"] = SENDER_EMAIL
        message["To"] = recipient_email

        message.attach(MIMEText(newspaper_content, "html"))

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
            logger.info(f"Sent newspaper to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(send_newspaper, 'interval', weeks=1)
scheduler.start()

@app.route('/')
def home():
    return render_template('index.html', stories=stories)

# Build directory compatibility routes
@app.route('/build/<path:filename>')
def serve_build_files(filename):
    """Serve files from build directory for deployment compatibility"""
    build_dir = os.path.join(os.path.dirname(__file__), 'build')
    try:
        return send_from_directory(build_dir, filename)
    except Exception:
        logger.warning(f"Build file not found: {filename}")
        return "File not found", 404

@app.route('/static/<path:filename>')  
def serve_static_files(filename):
    """Serve static files for deployment compatibility"""
    build_static_dir = os.path.join(os.path.dirname(__file__), 'build', 'static')
    if os.path.exists(build_static_dir):
        try:
            return send_from_directory(build_static_dir, filename)
        except Exception:
            pass
    return "File not found", 404

@app.route('/submit', methods=['POST'])
def submit_story():
    story_data = request.json
    title = story_data.get('title')
    content = story_data.get('content')
    author = story_data.get('author', 'Anonymous')
    if not title or not content:
        return jsonify({'error': 'Title and content are required.'}), 400
    stories.append({
        'title': title,
        'content': content,
        'author': author,
        'timestamp': datetime.now()
    })
    return jsonify({'message': 'Story submitted successfully'}), 200

@app.route('/subscribe', methods=['POST'])
def subscribe():
    sub_data = request.json
    email = sub_data.get('email')
    if not email:
        return jsonify({'error': 'Email is required.'}), 400
    if any(sub['email'] == email for sub in subscribers):
        return jsonify({'error': 'Email already subscribed.'}), 400
    subscribers.append({'email': email})
    return jsonify({'message': 'Subscribed successfully!'}) , 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)