# Blue Carbon Registry Backend - Setup Guide

## ✅ Files Created

All backend files have been successfully created:

```
backend/
├── main.py                          ✓ Main FastAPI application
├── database.py                      ✓ Database configuration
├── models.py                        ✓ SQLAlchemy models
├── schemas.py                       ✓ Pydantic schemas
├── requirements.txt                 ✓ Dependencies list
├── .env                            ✓ Environment variables
├── .env.example                    ✓ Environment template
├── README.md                        ✓ Documentation
├── test_api.py                     ✓ API test script
├── install_and_run.py              ✓ Auto-setup script
├── start_server.bat                ✓ Windows batch file
└── services/
    ├── __init__.py                 ✓ Services module
    ├── image_analysis.py           ✓ AI/ML image analysis
    ├── carbon_calculator.py        ✓ Carbon calculations
    ├── blockchain_service.py       ✓ Blockchain integration
    ├── verification_service.py     ✓ Verification workflow
    └── marketplace_service.py      ✓ Marketplace operations
```

## 🚀 Quick Start (3 Methods)

### Method 1: Using Python Script (Recommended)
```bash
cd backend
python install_and_run.py
```

### Method 2: Using Batch File (Windows)
```bash
cd backend
start_server.bat
```

### Method 3: Manual Installation
```bash
cd backend

# Install dependencies
pip install fastapi uvicorn[standard] sqlalchemy pydantic python-multipart aiofiles pillow httpx python-dateutil python-dotenv

# Run server
python main.py
```

## 📋 Step-by-Step Manual Setup

### Step 1: Open Terminal/Command Prompt
- Press `Win + R`, type `cmd`, press Enter
- Or use VS Code terminal: `Ctrl + ` (backtick)

### Step 2: Navigate to Backend Directory
```bash
cd "c:\Users\acer\OneDrive\Desktop\SIH prototype 25038 - Copy\backend"
```

### Step 3: Install Python Dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-multipart aiofiles pillow httpx python-dateutil python-dotenv
```

### Step 4: Run the Server
```bash
python main.py
```

### Step 5: Verify Server is Running
Open your browser and visit:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You should see:
```json
{
  "message": "Blue Carbon Registry API",
  "version": "1.0.0",
  "status": "operational"
}
```

## 🧪 Testing the API

### Option 1: Using the Test Script
Open a **NEW** terminal (keep the server running in the first one):
```bash
cd backend
python test_api.py
```

This will run a complete workflow test including:
- ✓ Project creation
- ✓ Satellite analysis
- ✓ Verification process
- ✓ Blockchain deployment
- ✓ GeoNFT minting
- ✓ Tokenization
- ✓ Marketplace listing
- ✓ Dashboard metrics

### Option 2: Using the Interactive Docs
1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"

### Option 3: Using cURL
```bash
# Health check
curl http://localhost:8000/health

# Create project
curl -X POST "http://localhost:8000/api/projects" ^
  -F "project_type=Mangrove Restoration" ^
  -F "location=New Delhi, India" ^
  -F "area=1.2" ^
  -F "start_date=2024-01-15" ^
  -F "end_date=2024-12-31" ^
  -F "description=Test project"
```

## 🔗 Connecting Frontend to Backend

### Update React App

In your React app, update the API base URL:

**Option 1: Create a config file**
```javascript
// src/config.js
export const API_BASE_URL = 'http://localhost:8000';
```

**Option 2: Use environment variable**
```javascript
// .env.local in React app
REACT_APP_API_URL=http://localhost:8000
```

**Option 3: Direct usage**
```javascript
// In your components
const API_URL = 'http://localhost:8000';

// Example: Create project
const createProject = async (projectData) => {
  const formData = new FormData();
  Object.keys(projectData).forEach(key => {
    formData.append(key, projectData[key]);
  });
  
  const response = await fetch(`${API_URL}/api/projects`, {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};
```

## 📊 Available API Endpoints

### Projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects` - List all projects

### Analysis
- `POST /api/analysis/site-image/{id}` - Upload & analyze image
- `POST /api/analysis/satellite/{id}` - Analyze satellite data

### Verification
- `POST /api/verification/{id}` - Create verification
- `PUT /api/verification/{id}/approve` - Approve verification
- `GET /api/verification/project/{id}` - Get verifications

### Blockchain
- `POST /api/blockchain/deploy/{id}` - Deploy contract
- `POST /api/blockchain/mint-geonft/{id}` - Mint GeoNFT

### Tokenization
- `POST /api/tokenization/create/{id}` - Create tokens
- `GET /api/tokenization/{id}` - Get token details

### Marketplace
- `POST /api/marketplace/list/{id}` - List on marketplace
- `GET /api/marketplace/listings` - Get all listings
- `GET /api/marketplace/statistics` - Market stats

### Dashboard
- `GET /api/dashboard/{id}` - Get dashboard metrics

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution**: Install missing dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-multipart
```

### Issue: "Port 8000 already in use"
**Solution**: Kill the process or use a different port
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or run on different port
python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8001)"
```

### Issue: CORS errors in browser
**Solution**: The backend already has CORS configured for localhost:3000 and localhost:3001. If you're using a different port, update the CORS_ORIGINS in `.env` file.

### Issue: Database errors
**Solution**: Delete the database file and restart
```bash
del blue_carbon_registry.db
python main.py
```

### Issue: Import errors
**Solution**: Make sure you're in the backend directory
```bash
cd "c:\Users\acer\OneDrive\Desktop\SIH prototype 25038 - Copy\backend"
python main.py
```

## 📝 What the Backend Provides

### ✅ Complete Features
1. **Project Management** - CRUD operations for carbon projects
2. **AI Image Analysis** - Simulated satellite and site image analysis
3. **Carbon Calculation** - Scientific carbon credit calculations
4. **Multi-Stage Verification** - Internal → Third-party → Legal
5. **Blockchain Integration** - Mock smart contract deployment
6. **GeoNFT Minting** - Location-bound NFT creation
7. **Tokenization** - ERC-20 compatible carbon tokens
8. **Marketplace** - Trading platform with statistics
9. **Dashboard** - Comprehensive metrics and analytics
10. **Database** - SQLite with all necessary models

### 🔄 Current Implementation
- **Mock AI/ML**: Simulated analysis (ready for TensorFlow/PyTorch)
- **Mock Blockchain**: Simulated transactions (ready for Aptos/Web3)
- **Real Database**: Fully functional SQLite database
- **Real API**: Complete REST API with FastAPI

### 🚀 Production Ready Features
To make it production-ready, you would need to:
1. Replace mock AI with real TensorFlow/PyTorch models
2. Integrate real blockchain (Aptos SDK or Web3.py)
3. Add authentication (JWT tokens)
4. Use PostgreSQL instead of SQLite
5. Add real satellite imagery APIs (Google Earth Engine, Sentinel Hub)
6. Deploy to cloud (AWS, Azure, Google Cloud)

## 💡 Next Steps

1. **Start the backend server** using one of the methods above
2. **Test the API** using the test script or interactive docs
3. **Connect your React frontend** to the backend
4. **Test the full workflow** from frontend to backend
5. **Customize** as needed for your requirements

## 📞 Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Visit http://localhost:8000/docs for API documentation
3. Review the logs in the terminal
4. Check the SETUP_GUIDE.md (this file)

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Server starts without errors
- ✅ http://localhost:8000 shows API info
- ✅ http://localhost:8000/docs shows interactive documentation
- ✅ Test script completes successfully
- ✅ Frontend can make API calls without CORS errors

---

**Backend is ready to use! Start the server and begin testing! 🚀**
