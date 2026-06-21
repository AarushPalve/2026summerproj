# FRC Strategic Dashboard - React + TypeScript + Python

A modern implementation of the FRC Strategic Dashboard with:
- **Frontend**: React with TypeScript
- **Backend**: Python (FastAPI)
- **Deployment**: Desktop (.exe) and Web (localhost)

## Features

- Real-time EPA/OPR/cOPR calculations
- ML-based match predictions
- 30-second hotspot sync
- Interactive data visualization
- Team comparison tools
- Match scheduling optimization

## Project Structure

```
frc_dashboard/
├── backend/                  # Python FastAPI backend
│   ├── src/                  # Backend source code
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core business logic
│   │   ├── models/            # Data models
│   │   ├── services/          # Service layer
│   │   └── main.py            # FastAPI app entry
│   └── requirements.txt       # Python dependencies
│
├── frontend/                 # React + TypeScript frontend
│   ├── public/               # Static files
│   ├── src/                  # Frontend source
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service layer
│   │   ├── types/            # TypeScript types
│   │   ├── utils/            # Utility functions
│   │   ├── App.tsx           # Main App component
│   │   ├── index.tsx         # Entry point
│   │   └── ...
│   ├── package.json          # Frontend dependencies
│   └── ...
│
├── data/                    # Data files
│   ├── models/               # ML models
│   └── raw/                  # Raw match data
│
├── scripts/                 # Deployment scripts
│   ├── build_desktop.py      # PyInstaller build script
│   └── run_dev.sh            # Development script
│
└── README.md                # This file
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd frc_dashboard

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up frontend
cd ../frontend
npm install
```

## Running the Application

### Development Mode (Web)

```bash
# Terminal 1: Backend
cd backend
python src/main.py

# Terminal 2: Frontend
cd frontend
npm start
```

The application will be available at http://localhost:3000

### Desktop Mode

```bash
# Build and run desktop application
python scripts/build_desktop.py
```

## Deployment

### Web Deployment

Build the frontend for production:

```bash
cd frontend
npm run build
```

The built files will be in `frontend/build/` and can be served by any static file server.

### Desktop Deployment

Create a standalone .exe file:

```bash
python scripts/build_desktop.py
```

This will create a bundled executable in the `dist/` directory.

## Architecture

### Backend (Python/FastAPI)

- **API Layer**: RESTful endpoints for data access
- **Core Layer**: Business logic for EPA/OPR/cOPR calculations
- **ML Service**: Match prediction using ONNX models
- **Data Service**: Hotspot sync and data management

### Frontend (React/TypeScript)

- **Components**: Reusable UI components
- **Pages**: Main application views
- **Services**: API communication layer
- **State Management**: React Context or Redux for global state

### Communication

The frontend communicates with the backend via REST API calls. All data processing happens on the backend, and the frontend displays the results.

## Key Features

### 1. EPA/OPR/cOPR Calculations

The system uses Recursive Least Squares (RLS) filtering to efficiently update team metrics as new match data arrives.

### 2. ML Predictions

Match predictions are made using an ensemble of DNN and Random Forest models, converted to ONNX format for efficient inference.

### 3. Hotspot Sync

The system supports 30-second hotspot sync to keep data up-to-date during events.

### 4. Real-time Updates

As matches are processed, the system provides real-time updates to team rankings and predictions.

## License

MIT License
