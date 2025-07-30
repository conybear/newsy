# Acta Diurna - Social Weekly Newspaper Network

A modern full-stack web application where friends create and share weekly newspaper editions together.

## 🌟 Features

### Phase 1: Authentication & Invitations
- ✅ **User Registration & Login**: JWT-based authentication system
- ✅ **Friend Invitations**: Email-based invitation system
- ✅ **User Management**: Profile management and friend networks

### Phase 2: Story Editor & Content System  
- ✅ **Rich Text Story Editor**: Bold, italic, underline formatting
- ✅ **Image Upload**: Up to 3 images per story (Base64 storage)
- ✅ **Auto-Save Drafts**: Automatic draft saving while writing
- ✅ **Story Submission**: One story per week submission system
- ✅ **Content Validation**: Title, headline, and content requirements

### Phase 3: Flipbook Newspaper Generation ⭐
- ✅ **Bidirectional Contributor Relationships**: Atomic MongoDB operations
- ✅ **Automated Weekly Editions**: Every Tuesday 8:00 AM EST
- ✅ **Flipbook Interface**: Classic newspaper-style reading experience
- ✅ **Story Aggregation**: Includes stories from all contributors
- ✅ **Archive System**: Browse past weekly editions

### Phase 4: Production Deployment 🚀
- ✅ **Render Deployment Configuration**: Production-ready setup
- ✅ **MongoDB Atlas Integration**: Cloud database configuration
- ✅ **Production Environment**: CORS, security, and optimization
- ✅ **Deployment Documentation**: Comprehensive deployment guide

## 🏗️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database with Motor async driver
- **JWT Authentication**: Secure token-based auth
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production

### Frontend  
- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Modern icon library

### Database
- **MongoDB Atlas**: Cloud-hosted MongoDB
- **Async Motor**: Python async MongoDB driver
- **Bidirectional Relationships**: Atomic operations for data consistency

### Deployment
- **Render**: Cloud application platform
- **GitHub Integration**: Continuous deployment
- **Environment Variables**: Secure configuration management

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Yarn package manager
- MongoDB Atlas account

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd acta-diurna
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file with your MongoDB connection
   echo "MONGO_URL=mongodb://localhost:27017" > .env
   echo "DB_NAME=acta_diurna" >> .env
   echo "SECRET_KEY=your-secret-key" >> .env
   
   # Start backend server
   uvicorn server:app --reload --port 8001
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   yarn install
   
   # Create .env file
   echo "REACT_APP_BACKEND_URL=http://localhost:8001/api" > .env
   
   # Start frontend server
   yarn start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001/api
   - API Documentation: http://localhost:8001/docs

## 📊 Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│────│   FastAPI Backend│────│  MongoDB Atlas  │
│                 │    │                  │    │                 │
│ • Authentication│    │ • JWT Auth       │    │ • Users         │
│ • Story Editor  │    │ • Story Management│    │ • Stories       │
│ • Flipbook UI   │    │ • Newspaper Gen  │    │ • Invitations   │
│ • Navigation    │    │ • Friend System  │    │ • Newspapers    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🗂️ Project Structure

```
acta-diurna/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main FastAPI application
│   ├── models.py           # Pydantic data models
│   ├── database.py         # MongoDB connection
│   ├── auth.py             # JWT authentication
│   ├── utils.py            # Utility functions
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── utils/          # Utility functions
│   │   └── App.js          # Main React app
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
├── render.yaml             # Render deployment config
├── DEPLOYMENT.md           # Deployment guide
└── README.md               # This file
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/users/me` - Get current user info

### Invitations & Contributors
- `POST /api/invitations/send` - Send invitation
- `GET /api/invitations/received` - Get received invitations
- `POST /api/contributors/add` - Add bidirectional contributor
- `GET /api/contributors/my` - Get my contributors

### Stories
- `GET /api/stories/status` - Get submission status
- `POST /api/stories/draft` - Save story draft
- `GET /api/stories/draft` - Get saved draft
- `POST /api/stories/submit` - Submit story
- `GET /api/stories/my` - Get my stories
- `GET /api/stories/weekly/{week}` - Get weekly stories

### Newspapers
- `GET /api/newspapers/current` - Get current week's newspaper
- `GET /api/newspapers/week/{week}` - Get specific week's newspaper
- `GET /api/newspapers/archive` - Get newspaper archive
- `POST /api/newspapers/regenerate` - Regenerate current newspaper

### Health
- `GET /api/health` - Health check endpoint

## 🌐 Production Deployment

### Deploy to Render

1. **Prerequisites**
   - GitHub repository with your code
   - MongoDB Atlas cluster
   - Render account

2. **Deployment Steps**
   ```bash
   # 1. Push to GitHub
   git add .
   git commit -m "Ready for production deployment"
   git push origin main
   
   # 2. Create services on Render using render.yaml
   # 3. Configure environment variables
   # 4. Deploy and test
   ```

3. **Environment Variables**
   
   **Backend:**
   - `MONGO_URL`: MongoDB Atlas connection string
   - `SECRET_KEY`: JWT secret key
   - `ENVIRONMENT`: "production"
   
   **Frontend:**
   - `REACT_APP_BACKEND_URL`: Backend service URL

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).

## 🧪 Testing

The application includes comprehensive testing coverage:

- ✅ **Authentication System**: Registration, login, JWT validation
- ✅ **Story Management**: Creation, drafts, submission, validation
- ✅ **Contributor System**: Bidirectional relationships, invitation workflow
- ✅ **Newspaper Generation**: Story aggregation, flipbook creation
- ✅ **Business Rules**: One story per week, image limits, deadlines

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt password hashing
- **CORS Protection**: Environment-specific CORS configuration
- **Input Validation**: Pydantic model validation
- **Environment Variables**: Secure configuration management

## 📈 Performance Optimizations

- **Database Indexes**: Optimized MongoDB queries
- **Async Operations**: Non-blocking database operations
- **Static File Serving**: Optimized frontend serving
- **Connection Pooling**: Efficient database connections
- **Atomic Operations**: Consistent bidirectional relationships

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: See DEPLOYMENT.md for deployment help
- **Issues**: Create GitHub issues for bugs/features
- **API Documentation**: Visit `/docs` endpoint for interactive API docs

## 🎯 Future Enhancements

- **Email Notifications**: Automated weekly newsletter emails
- **Image Storage**: Migrate from Base64 to AWS S3
- **Mobile App**: React Native mobile application
- **Advanced Editor**: More rich text formatting options
- **Social Features**: Comments, likes, sharing
- **Analytics**: Usage statistics and insights

---

**Acta Diurna** - Bringing friends together through shared storytelling, one week at a time. 📰✨
