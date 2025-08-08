# Newsy - Digital Newspaper Platform Deployment Guide

## 🎉 Congratulations! Your Newsy Platform is Ready

Your Newsy digital newspaper platform has been successfully deployed and is fully functional. This guide will help you configure the remaining features and customize your deployment.

## 🚀 Current Status

✅ **Fully Operational Features:**
- Homepage with story display
- Story submission form with validation
- Interactive flipbook newspaper viewer
- Newsletter subscription management
- Responsive design for all devices
- MongoDB data persistence
- Background scheduler setup

✅ **Working Endpoints:**
- `GET /api/` - API status
- `GET /api/stories` - Get all stories
- `POST /api/stories` - Submit new story
- `GET /api/stories/weekly` - Get weekly stories
- `GET /api/newspaper/flipbook` - Flipbook viewer
- `POST /api/subscribe` - Newsletter subscription
- `GET /api/subscribers` - Subscriber management

## 📧 Email Newsletter Configuration

To enable the weekly email newsletter feature, you need to configure your email settings:

### 1. Update Environment Variables

Edit `/app/backend/.env` and replace the placeholder values:

```env
# Email Configuration for Newsletter
NEWSLETTER_EMAIL="your-actual-email@gmail.com"
NEWSLETTER_PASSWORD="your-app-specific-password"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
```

### 2. Gmail Setup (Recommended)

1. **Create a Gmail Account** (or use existing):
   - Go to gmail.com and create an account for your newsletter
   - Example: `newsyweekly@gmail.com`

2. **Enable 2-Factor Authentication**:
   - Go to Google Account settings
   - Security → 2-Step Verification → Turn On

3. **Generate App Password**:
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
   - Use this 16-character password (not your regular password)

4. **Update Configuration**:
   ```env
   NEWSLETTER_EMAIL="newsyweekly@gmail.com"
   NEWSLETTER_PASSWORD="abcd efgh ijkl mnop"  # 16-character app password
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT="587"
   ```

### 3. Alternative Email Providers

**Outlook/Hotmail:**
```env
SMTP_SERVER="smtp-mail.outlook.com"
SMTP_PORT="587"
```

**Yahoo:**
```env
SMTP_SERVER="smtp.mail.yahoo.com"
SMTP_PORT="587"
```

**Custom SMTP:**
```env
SMTP_SERVER="your-smtp-server.com"
SMTP_PORT="587"  # or 25, 465 depending on your provider
```

## 🗂️ Database Collections

Your MongoDB database (`newsy_database`) contains:

- **stories**: All submitted stories with title, content, author, and timestamp
- **subscribers**: Email addresses with subscription dates

## 📅 Newsletter Schedule

The newsletter is automatically sent every **Monday at 9:00 AM** containing all stories from the previous week. The schedule can be modified in `/app/backend/server.py`:

```python
scheduler.add_job(
    send_newsletter,
    'cron',
    day_of_week='mon',  # Change to desired day
    hour=9,             # Change to desired hour
    minute=0
)
```

## 🔧 Manual Newsletter Testing

To test the newsletter system:

1. **Add Test Subscriber**:
   ```bash
   curl -X POST http://localhost:8001/api/subscribe \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
   ```

2. **Send Newsletter Manually**:
   ```bash
   curl -X POST http://localhost:8001/api/newsletter/send
   ```

## 🎨 Customization Options

### 1. Branding
- Update the newspaper name in `/app/frontend/src/App.js`
- Change colors in `/app/frontend/src/App.css`
- Modify the hero section messaging

### 2. Flipbook Styling
- Edit the flipbook HTML template in `/app/backend/server.py`
- Customize colors, fonts, and layout in the `compile_newspaper_flipbook()` function

### 3. Email Template
- The newsletter uses the same flipbook HTML template
- Modify the template to customize email appearance

## 🔒 Security Recommendations

1. **Environment Variables**: Never commit actual email credentials to git
2. **Email Limits**: Gmail has daily sending limits (500 emails/day for free accounts)
3. **Monitoring**: Check `/var/log/supervisor/backend*.log` for email sending logs
4. **Backup**: Regularly backup your MongoDB database

## 📱 Mobile Optimization

The platform is fully mobile-responsive with:
- Touch-friendly navigation
- Optimized flipbook viewing
- Mobile-first form design
- Responsive image handling

## 🎯 Key Features Highlights

### Interactive Flipbook
- **Page Navigation**: Previous/Next buttons + keyboard arrows
- **Page Indicators**: Shows current page and total pages
- **Mobile Support**: Touch navigation and responsive design
- **Print Ready**: Clean layout for printing

### Story Management
- **Rich Text Support**: Full paragraph formatting
- **Author Attribution**: Optional author names with Anonymous fallback
- **Timestamp Display**: Automatic date/time tracking
- **Content Validation**: Prevents empty submissions

### Newsletter System
- **Duplicate Prevention**: Blocks multiple subscriptions
- **Weekly Compilation**: Automatic story collection
- **Email Validation**: Ensures valid email addresses
- **Subscriber Management**: Admin interface for subscriber lists

## 🚀 Going Live

Your platform is production-ready! To go live:

1. Configure email settings (as described above)
2. Add your own content and stories
3. Share the URL with your community
4. Monitor the logs for any issues

## 🆘 Troubleshooting

### Email Not Sending
- Check email credentials in `.env`
- Verify SMTP settings for your provider
- Check backend logs: `tail -f /var/log/supervisor/backend*.log`

### Stories Not Appearing
- Check MongoDB connection
- Verify API endpoints are responding
- Clear browser cache and refresh

### Flipbook Issues
- Ensure stories exist in database
- Check browser JavaScript console for errors
- Test with multiple browsers

## 📞 Support

Your Newsy platform has been fully implemented with all features from your original Flask repository, enhanced with modern React frontend and robust FastAPI backend. The hybrid approach gives you the best of both worlds!

**Happy Publishing! 📰✨**