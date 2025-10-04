# 🚀 QUICK START GUIDE

## ✅ Everything is Ready! Here's What You Have:

### 📦 Complete System Components

```
✅ Backend (Python FastAPI)     - 20+ API endpoints
✅ Frontend (React)              - Complete UI with 6 components  
✅ Smart Contracts (Move)        - Aptos blockchain contracts
✅ Database (SQLite)             - All models configured
✅ Services (7 modules)          - AI, Blockchain, Verification, etc.
```

---

## 🎯 START IN 3 STEPS

### Step 1: Open Terminal
Press `Win + R`, type `cmd`, press Enter

### Step 2: Navigate to Project
```bash
cd "c:\Users\acer\OneDrive\Desktop\SIH prototype 25038 - Copy"
```

### Step 3: Run Both Servers
```bash
start_both.bat
```

**That's it!** Two windows will open:
- Backend Server (black window)
- Frontend Server (black window)

Wait 30 seconds, then open browser: **http://localhost:3000**

---

## 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main application UI |
| **Backend** | http://localhost:8000 | API root |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **ReDoc** | http://localhost:8000/redoc | Alternative API docs |

---

## 🎮 What You Can Do Right Now

### 1. Create a Carbon Credit Project
- Go to http://localhost:3000
- Fill in project details (type, location, area, dates)
- Upload a site image
- See satellite analysis results

### 2. Complete Verification Process
- Click "Continue to Verification"
- Review analysis summary
- Proceed to Third-Party Verification
- Complete Legal Compliance

### 3. Deploy to Blockchain
- Click "Proceed to Blockchain Registry"
- See transaction confirmation
- View GeoNFT creation

### 4. Tokenize Carbon Credits
- Click "Proceed to Tokenization"
- See ERC-20 tokens created
- View revenue distribution

### 5. List on Marketplace
- Click "List on Carbon Marketplace"
- See market statistics
- View environmental impact

### 6. Monitor Impact
- Click "List on Global Marketplace"
- View comprehensive dashboard
- See real-time metrics

---

## 🧪 Test the API

Open a **NEW** terminal (keep servers running):

```bash
cd backend
python test_api.py
```

This tests the complete workflow automatically!

---

## 📊 What's Working

### ✅ Fully Functional (No Additional Setup)
- Complete UI/UX flow
- All API endpoints
- Database operations
- Image upload and storage
- Carbon credit calculations
- Multi-stage verification
- Simulated blockchain (instant, no gas)
- Marketplace operations
- Impact dashboard
- Revenue distribution

### ⚡ Enhanced Mode (Optional)
To enable **real Aptos blockchain**:

```bash
cd backend
pip install aptos-sdk
python main.py
```

Then restart and you'll have:
- Real blockchain transactions
- Actual GeoNFT minting on Aptos
- On-chain verification
- Real transaction hashes

---

## 🎨 User Interface Flow

```
1. Initial Assessment
   ↓
2. Verification (Internal)
   ↓
3. Third-Party Verification
   ↓
4. Legal Compliance
   ↓
5. Blockchain Registry
   ↓
6. Smart Contracts (Tokenization)
   ↓
7. Carbon Marketplace
   ↓
8. Impact Dashboard
```

---

## 🔧 Troubleshooting

### Backend won't start?
```bash
cd backend
pip install fastapi uvicorn sqlalchemy pydantic python-multipart
python main.py
```

### Frontend won't start?
```bash
cd carbon-assessment
npm install
npm start
```

### Port already in use?
Kill the process:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### CORS errors?
Backend is already configured for localhost:3000. If using different port, update `backend/.env`:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `start_both.bat` | Start both servers |
| `start_backend.bat` | Start backend only |
| `start_frontend.bat` | Start frontend only |
| `backend/test_api.py` | Test all API endpoints |
| `check_integration.py` | Verify integration |
| `INTEGRATION_STATUS.md` | Detailed status report |
| `FINAL_SUMMARY.md` | Complete documentation |

---

## 🎯 Example Workflow

### Create Your First Project:

1. **Start servers**: Run `start_both.bat`

2. **Open app**: http://localhost:3000

3. **Fill form**:
   - Project Type: "Mangrove Restoration"
   - Location: "New Delhi, India"
   - Area: "1.2" hectares
   - Start Date: "2024-01-15"
   - End Date: "2024-12-31"
   - Description: "Restoration project"

4. **Upload image**: Click "Select Image" and choose any image

5. **Wait for analysis**: Progress bar shows satellite analysis

6. **Continue**: Click "Continue to Verification"

7. **Follow workflow**: Click through each step

8. **View results**: See your project on blockchain and marketplace!

---

## 📞 API Examples

### Create Project (cURL)
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -F "project_type=Mangrove Restoration" \
  -F "location=New Delhi, India" \
  -F "area=1.2" \
  -F "start_date=2024-01-15" \
  -F "end_date=2024-12-31" \
  -F "description=Test project"
```

### Get Project
```bash
curl "http://localhost:8000/api/projects/1"
```

### Deploy to Blockchain
```bash
curl -X POST "http://localhost:8000/api/blockchain/deploy/1"
```

### Get Dashboard
```bash
curl "http://localhost:8000/api/dashboard/1"
```

---

## 🎓 Smart Contract Info

**Location**: `aptos-contracts/sources/carbon_credit.move`

**Features**:
- Carbon project registration
- GeoNFT (location-bound NFT) minting
- Credit transfer and retirement
- Verification tracking
- Event emission

**To Deploy** (Optional):
```bash
# Install Aptos CLI
# https://aptos.dev/cli-tools/aptos-cli-tool/install-aptos-cli

cd aptos-contracts
aptos init
aptos move compile
aptos move publish
```

---

## 💡 Tips

1. **Keep both terminals open** while using the app
2. **Use Chrome/Edge** for best experience
3. **Check API docs** at http://localhost:8000/docs for all endpoints
4. **Run test script** to verify everything works
5. **Check INTEGRATION_STATUS.md** for detailed info

---

## 🎉 You're All Set!

Your complete Blue Carbon Registry system is ready to use!

**Just run**: `start_both.bat`

**Then open**: http://localhost:3000

**Enjoy!** 🌱🌍💚

---

## 📚 More Documentation

- `INTEGRATION_STATUS.md` - Detailed integration status
- `FINAL_SUMMARY.md` - Complete system documentation
- `backend/README.md` - Backend API documentation
- `aptos-contracts/README.md` - Smart contract guide

---

**Last Updated**: 2025-10-04  
**Status**: ✅ Ready to Use  
**Mode**: Demo (upgrade to Production with `pip install aptos-sdk`)
