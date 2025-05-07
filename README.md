# newsy
from flask import Flask, request, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

app = Flask(__name__)

# In-memory storage for stories and subscribers
stories = []
subscribers = []

# Helper function to compile a weekly newspaper
def compile_newspaper():
    current_time = datetime.now()
    week_ago = current_time - timedelta(days=7)

    # Filter stories from the past week
    weekly_stories = [story for story in stories if story['timestamp'] >= week_ago]

    # Generate newspaper content
    newspaper_content = "<h1>Weekly Newspaper</h1>"
    newspaper_content += "<p>Here are the stories from the past week:</p><ul>"
    for story in weekly_stories:
        newspaper_content += f"<li><h3>{story['title']}</h3><p><strong>Author:</strong> {story['author']}</p><p>{story['content']}</p></li>"
    newspaper_content += "</ul>"

    return newspaper_content

# Helper function to send the newspaper via email
def send_newspaper():
    newspaper_content = compile_newspaper()
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"

    for subscriber in subscribers:
        recipient_email = subscriber['email']
        message = MIMEMultipart("alternative")
        message["Subject"] = "Weekly Newspaper"
        message["From"] = sender_email
        message["To"] = recipient_email

        # Attach the newspaper content
        message.attach(MIMEText(newspaper_content, "html"))

        # Send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())

# Schedule the weekly newspaper job
scheduler = BackgroundScheduler()
scheduler.add_job(send_newspaper, 'interval', weeks=1)
scheduler.start()

# Home route to display all stories
@app.route('/')
def home():
    return render_template('index.html', stories=stories)

# API route to submit a story
@app.route('/submit', methods=['POST'])
def submit_story():
    story_data = request.json
    title = story_data.get('title')
    content = story_data.get('content')
    author = story_data.get('author', 'Anonymous')
