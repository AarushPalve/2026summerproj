# FRC Dashboard Application - Setup and Run Instructions

## Quick Start

### 1. Backend Setup and Run

The backend is a FastAPI application that serves the API and can also serve the frontend.

#### Prerequisites
- Python 3.10+
- Required Python packages (already installed globally)

#### Run the Backend

```bash
# Navigate to the backend directory
cd frc_dashboard/backend

# Run the backend server
python src/main.py --port 8000
```

The backend will start on `http://localhost:8000` and will automatically:
- Serve the static HTML page from `frc_dashboard/static/index.html`
- Provide API endpoints under `/api/v1/*`
- Serve API documentation at `/api/docs`

### 2. Frontend Setup (Optional)

The React frontend is optional. If you want to build and use it:

#### Prerequisites
- Node.js 16+
- npm or yarn

#### Build the Frontend

```bash
# Navigate to the frontend directory
cd frc_dashboard/frontend

# Install dependencies (already done)
npm install

# Build the frontend
npm run build
```

After building, the frontend files will be in `frc_dashboard/frontend/build/` and the backend will automatically serve them.

### 3. Access the Application

Once the backend is running:

- **Static Dashboard**: `http://localhost:8000/`
- **API Documentation**: `http://localhost:8000/api/docs`
- **Interactive API Explorer**: `http://localhost:8000/api/redoc`
- **Health Check**: `http://localhost:8000/health`

## API Endpoints

### Matches API (`/api/v1/matches/`)
- `POST /upload` - Upload match data CSV
- `GET /teams` - Get current team metrics
- `POST /update` - Update with new match
- `GET /components` - Get available score components
- `GET /history` - Get match history

### Predictions API (`/api/v1/predictions/`)
- `POST /` - Predict match outcome
- `POST /batch` - Batch predict multiple matches
- `GET /health` - Check ML pipeline health

### Teams API (`/api/v1/teams/`)
- Endpoints for team-specific operations

### Stats API (`/api/v1/stats/`)
- `GET /system` - Get system information
- `GET /calculations` - Get calculation statistics
- `GET /distribution` - Get metric distributions

## Development Mode

For development with auto-reload:

```bash
cd frc_dashboard/backend
python src/main.py --port 8000 --reload
```

## Troubleshooting

### Backend Issues
- Ensure all Python dependencies are installed
- Check that model files are in `frc_dashboard/backend/data/models/`
- Verify the ONNX data file is present

### Frontend Issues
- If build fails due to linting errors, you can use the static HTML page
- The static page provides basic functionality and API documentation

## Data Files

The application expects:
- Match data CSV files in `frc_dashboard/backend/data/raw/`
- Model files in `frc_dashboard/backend/data/models/`
- ONNX models and their associated `.data` files

## Current Status

✅ Backend is fully functional
✅ API endpoints are working
✅ ML pipeline is initialized and ready
✅ Static HTML dashboard is available
⚠️ React frontend build has linting issues (optional)

The application is ready to use with the static interface and full API functionality!