# Blue Carbon Registry - Backend API

A comprehensive FastAPI backend for the Blue Carbon Registry application, supporting carbon credit registration, verification, blockchain integration, and marketplace operations.

## Features

- ✅ **Project Management**: Create and manage carbon credit projects
- ✅ **AI-Powered Analysis**: Satellite imagery and site image analysis
- ✅ **Carbon Calculation**: Scientific carbon credit calculation based on IS 14064-2:2019
- ✅ **Multi-Stage Verification**: Internal, third-party, and legal compliance verification
- ✅ **Blockchain Integration**: Smart contract deployment and GeoNFT minting (Aptos/Ethereum)
- ✅ **Tokenization**: ERC-20 compatible carbon credit tokens
- ✅ **Marketplace**: Trading platform with market statistics
- ✅ **Impact Dashboard**: Real-time environmental and community metrics

## Tech Stack

- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLAlchemy with SQLite (PostgreSQL ready)
- **Validation**: Pydantic
- **Blockchain**: Aptos SDK / Web3.py (mock implementation included)
- **AI/ML**: TensorFlow/PyTorch ready (mock implementation included)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env with your configuration
```

### 3. Run the Server

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /` - API information
- `GET /health` - Health check

### Projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{project_id}` - Get project details
- `GET /api/projects` - List all projects

### Image Analysis
- `POST /api/analysis/site-image/{project_id}` - Upload and analyze site image
- `POST /api/analysis/satellite/{project_id}` - Analyze satellite data

### Verification
- `POST /api/verification/{project_id}` - Create verification record
- `PUT /api/verification/{verification_id}/approve` - Approve verification
- `GET /api/verification/project/{project_id}` - Get project verifications

### Blockchain
- `POST /api/blockchain/deploy/{project_id}` - Deploy smart contract
- `POST /api/blockchain/mint-geonft/{project_id}` - Mint GeoNFT

### Tokenization
- `POST /api/tokenization/create/{project_id}` - Create carbon tokens
- `GET /api/tokenization/{project_id}` - Get carbon credit details

### Marketplace
- `POST /api/marketplace/list/{project_id}` - List credits on marketplace
- `GET /api/marketplace/listings` - Get all listings
- `GET /api/marketplace/statistics` - Get market statistics

### Dashboard
- `GET /api/dashboard/{project_id}` - Get comprehensive dashboard metrics

## Project Structure

```
backend/
├── main.py                          # FastAPI application entry point
├── database.py                      # Database configuration
├── models.py                        # SQLAlchemy models
├── schemas.py                       # Pydantic schemas
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── README.md                        # This file
├── services/                        # Business logic services
│   ├── __init__.py
│   ├── image_analysis.py           # AI/ML image analysis
│   ├── carbon_calculator.py        # Carbon credit calculations
│   ├── blockchain_service.py       # Blockchain integration
│   ├── verification_service.py     # Verification workflow
│   └── marketplace_service.py      # Marketplace operations
└── uploads/                         # File uploads directory
    └── site_images/                # Uploaded site images
```

## Database Models

### Project
- Project information, location, area
- Image paths and analysis results
- Carbon credit estimates
- Blockchain addresses

### Verification
- Multi-stage verification records
- Verifier information
- Status tracking

### BlockchainTransaction
- Transaction hashes and details
- Contract addresses
- Gas usage and fees

### CarbonCredit
- Total and available credits
- Pricing and valuation
- Token standards

### MarketListing
- Marketplace listings
- Pricing and availability
- Transaction history

## Example Usage

### 1. Create a Project

```bash
curl -X POST "http://localhost:8000/api/projects" \
  -F "project_type=Mangrove Restoration" \
  -F "location=New Delhi, India" \
  -F "area=1.2" \
  -F "start_date=2024-01-15" \
  -F "end_date=2024-12-31" \
  -F "description=Mangrove restoration project" \
  -F "latitude=28.6139" \
  -F "longitude=77.2090"
```

### 2. Upload Site Image

```bash
curl -X POST "http://localhost:8000/api/analysis/site-image/1" \
  -F "image=@site_photo.jpg"
```

### 3. Analyze Satellite Data

```bash
curl -X POST "http://localhost:8000/api/analysis/satellite/1"
```

### 4. Create Verification

```bash
curl -X POST "http://localhost:8000/api/verification/1" \
  -F "verification_type=internal" \
  -F "verifier_name=Dr. Manas Negi" \
  -F "notes=Initial verification complete"
```

### 5. Deploy to Blockchain

```bash
curl -X POST "http://localhost:8000/api/blockchain/deploy/1"
```

## Integration with Frontend

Update your React app to connect to the backend:

```javascript
// In your React components
const API_BASE_URL = 'http://localhost:8000';

// Create project
const createProject = async (projectData) => {
  const formData = new FormData();
  Object.keys(projectData).forEach(key => {
    formData.append(key, projectData[key]);
  });
  
  const response = await fetch(`${API_BASE_URL}/api/projects`, {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};

// Upload image
const uploadImage = async (projectId, imageFile) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await fetch(
    `${API_BASE_URL}/api/analysis/site-image/${projectId}`,
    {
      method: 'POST',
      body: formData
    }
  );
  
  return response.json();
};
```

## Production Deployment

### Using PostgreSQL

1. Install PostgreSQL
2. Create database: `createdb blue_carbon_registry`
3. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/blue_carbon_registry
   ```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

- Set `DEBUG=False`
- Use strong `SECRET_KEY`
- Configure proper database URL
- Set up HTTPS/SSL
- Configure proper CORS origins

## Advanced Features (To Implement)

### Real AI/ML Integration

Uncomment AI dependencies in `requirements.txt` and implement:
- TensorFlow/PyTorch models for image analysis
- Satellite imagery processing with Google Earth Engine
- NDVI calculation from Sentinel-2 data

### Real Blockchain Integration

Uncomment blockchain dependencies and implement:
- Aptos SDK for Move smart contracts
- Web3.py for Ethereum integration
- Wallet connection and transaction signing

### Background Tasks

Implement Celery for:
- Async satellite data processing
- Scheduled monitoring updates
- Email notifications

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the code comments
- Check the example requests above

## License

MIT License - See LICENSE file for details
