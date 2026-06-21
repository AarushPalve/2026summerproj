# FRC Strategic Dashboard - Proxy Server Configuration

## Overview
Successfully configured the FRC Strategic Dashboard to be accessible through a single localhost link at http://localhost:8000.

## Configuration Details

### Backend Server
- **Framework**: FastAPI with Uvicorn
- **Port**: 8000
- **Entry Point**: `frc_dashboard/backend/src/main.py`

### Proxy Routing
The backend server now serves both:
1. **Static files** (frontend) from the root path `/`
2. **API endpoints** from `/api/v1/*`

### Key Changes Made

1. **Static File Serving** (`main.py`):
   - Added logic to serve static files from either:
     - `frontend/build/` (if React frontend is built)
     - `static/` (fallback static HTML page)
   - Implemented SPA (Single Page Application) routing
   - Catch-all route serves `index.html` for all non-API paths

2. **Route Prioritization**:
   - API routes are registered before static file routes
   - Health check endpoint (`/health`) works correctly
   - API documentation available at `/api/docs`

3. **Static HTML Page**:
   - Created `static/index.html` as a fallback
   - Provides information about available API endpoints
   - Includes links to API documentation

## Accessible Endpoints

### Static Content
- `http://localhost:8000/` - Serves static HTML page

### Health Check
- `http://localhost:8000/health` - API health status

### API Endpoints
- `http://localhost:8000/api/v1/teams/` - Team information
- `http://localhost:8000/api/v1/matches/teams` - Match data
- `http://localhost:8000/api/v1/predictions/health` - Prediction health
- `http://localhost:8000/api/v1/stats/system` - System statistics

### API Documentation
- `http://localhost:8000/api/docs` - Interactive Swagger UI
- `http://localhost:8000/api/redoc` - Alternative ReDoc documentation

## How to Run

### Start the Backend Server
```bash
cd frc_dashboard/backend/src
python main.py --port 8000 --host 0.0.0.0
```

The server will automatically:
1. Check for a built React frontend in `frontend/build/`
2. Fall back to serving static HTML from `static/`
3. Serve all API endpoints from `/api/v1/*`

### Build the React Frontend (Optional)
To serve the full React application instead of the static HTML page:

```bash
cd frc_dashboard/frontend
npm install
npm run build
```

Then restart the backend server. It will automatically detect and serve the built frontend.

## Testing

Run the comprehensive test suite:
```bash
./final_test.sh
```

All tests should pass, confirming:
- Static files are served from root
- API endpoints are accessible
- API documentation is available
- Health checks work correctly

## Notes

- The proxy configuration ensures that API routes take precedence over static file routes
- The catch-all route only serves `index.html` for non-API, non-static paths
- CORS is enabled for all origins to support development
- The configuration supports both development (React dev server) and production (built frontend) modes

## Future Improvements

1. **Frontend Build**: Complete the React frontend build process
2. **Authentication**: Add authentication middleware for protected endpoints
3. **Caching**: Implement caching for static assets
4. **Load Balancing**: Configure for multiple backend instances
5. **HTTPS**: Add SSL/TLS support for secure connections
