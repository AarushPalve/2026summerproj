# FRC Dashboard Frontend

A production-grade React/TypeScript frontend for the FRC Strategic Dashboard application.

## 📁 Project Structure

```
frontend/
├── public/                  # Static assets
├── src/
│   ├── components/          # Reusable UI components
│   ├── context/             # React context providers
│   ├── hooks/               # Custom React hooks
│   ├── pages/               # Main application pages
│   ├── services/            # API service layer
│   ├── types/               # TypeScript type definitions
│   ├── utils/               # Utility functions
│   ├── App.tsx              # Main application component
│   ├── index.tsx            # Application entry point
│   └── ...
├── package.json            # Frontend dependencies
└── README.md               # This file
```

## 🚀 Features

### Core Functionality
- **Real-time Data Dashboard**: Overview of system status and key metrics
- **Team Management**: Browse, search, and compare teams with detailed statistics
- **Match Predictions**: ML-powered match outcome predictions with confidence scores
- **Data Upload**: Drag-and-drop interface for uploading match data files
- **System Settings**: Configure application preferences and monitor system health

### Technical Features
- **TypeScript**: Strong typing throughout the application
- **Material-UI**: Professional UI components with dark theme support
- **React Router**: Client-side routing with code splitting
- **Context API**: Global state management
- **Custom Hooks**: Reusable logic for data fetching and error handling
- **Responsive Design**: Works on desktop and tablet devices

## 📊 Pages

### 1. Dashboard
- System overview with key metrics
- EPA/OPR statistics visualization
- Team performance summaries
- Real-time data updates

### 2. Teams
- Comprehensive team directory
- Advanced search and filtering
- Sortable columns (EPA, OPR, matches played)
- Team comparison functionality
- Pagination for large datasets

### 3. Predictions
- Alliance selection interface
- Match type configuration (QM, SF, F)
- ML model health monitoring
- Detailed prediction breakdowns
- Confidence visualization

### 4. Upload
- Drag-and-drop file upload
- CSV/JSON format support
- Upload progress tracking
- Batch file processing
- Error handling and validation

### 5. Settings
- Theme configuration (dark/light mode)
- Auto-refresh settings
- API endpoint configuration
- System status monitoring
- Application information

## 🔧 Technical Stack

### Core Technologies
- **React 18**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Material-UI v5**: UI component library
- **React Router v6**: Client-side routing
- **Axios**: HTTP client for API communication
- **React Dropzone**: File upload functionality

### Development Tools
- **ESLint**: Code linting
- **Prettier**: Code formatting
- **Create React App**: Build configuration
- **TypeScript ESLint**: TypeScript-specific linting rules

## 📦 Dependencies

### Production Dependencies
- `@emotion/react`, `@emotion/styled`: CSS-in-JS styling
- `@mui/material`, `@mui/icons-material`: Material-UI components and icons
- `@mui/x-data-grid`: Advanced data grid component
- `axios`: HTTP client
- `react`, `react-dom`: React core libraries
- `react-dropzone`: File upload functionality
- `react-router-dom`: Client-side routing

### Development Dependencies
- `@types/react`, `@types/react-dom`: TypeScript types
- `@typescript-eslint/eslint-plugin`, `@typescript-eslint/parser`: TypeScript ESLint integration
- `eslint`, `eslint-plugin-react`: Linting tools
- `prettier`: Code formatting
- `typescript`: TypeScript compiler

## 🛠️ Setup & Installation

### Prerequisites
- Node.js 16+ (LTS recommended)
- npm 7+ or yarn 1.22+
- Backend API server running (see main README)

### Installation

```bash
# Navigate to frontend directory
cd frc_dashboard/frontend

# Install dependencies
npm install
# or
 yarn install
```

### Configuration

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
# or use the proxy setup in package.json
```

The application is configured to proxy API requests to `http://localhost:8000` by default.

## 🚀 Running the Application

### Development Mode

```bash
npm start
# or
 yarn start
```

This will:
- Start the development server on `http://localhost:3000`
- Enable hot module replacement
- Proxy API requests to the backend
- Open the browser automatically

### Production Build

```bash
npm run build
# or
 yarn build
```

This creates an optimized production build in the `build/` directory.

### Running Tests

```bash
npm test
# or
 yarn test
```

### Code Formatting

```bash
npm run format
# or
 yarn format
```

### Linting

```bash
npm run lint
# or
 yarn lint
```

## 📱 Development Workflow

### API Integration

The frontend communicates with the FastAPI backend through the following endpoints:

- **Teams**: `/api/v1/teams`
- **Predictions**: `/api/v1/predictions`
- **Matches**: `/api/v1/matches`
- **Stats**: `/api/v1/stats`
- **Health**: `/health`

### State Management

The application uses React Context for global state:

- **AppContext**: Manages backend health, theme settings, and auto-refresh
- **Custom Hooks**: `useDataFetching`, `useApiError` for reusable logic

### Error Handling

Comprehensive error handling is implemented:

- API error interception with Axios
- User-friendly error messages
- Loading states for async operations
- Graceful degradation when backend is unavailable

## 🎨 UI/UX Design

### Design System

- **Color Scheme**: Dark theme with FRC-inspired colors (red/blue alliances)
- **Typography**: Roboto font family
- **Spacing**: Consistent 8px grid system
- **Components**: Material-UI components with custom styling

### Responsive Design

- Desktop-first approach
- Responsive grid layouts
- Adaptive component sizing
- Mobile-friendly navigation

## 🔄 Data Flow

1. **User Interaction**: User navigates pages and triggers actions
2. **API Requests**: Frontend makes HTTP requests to backend
3. **Data Processing**: Backend processes requests and returns JSON
4. **State Updates**: Frontend updates React state
5. **UI Rendering**: Components re-render with new data

## 📈 Performance Optimization

- **Code Splitting**: React.lazy for route-based code splitting
- **Memoization**: React.memo for component optimization
- **Debouncing**: Search inputs and rapid actions
- **Caching**: API response caching where appropriate
- **Bundle Analysis**: Webpack bundle analyzer for optimization

## 🧪 Testing Strategy

### Current Testing
- Component rendering tests
- API integration tests
- Error boundary testing
- Form validation testing

### Future Testing Enhancements
- End-to-end testing with Cypress
- Unit tests for utility functions
- Integration tests for complex flows
- Accessibility testing

## 📁 File Structure Details

### Components
- **Navbar.tsx**: Main navigation component
- **LoadingSpinner.tsx**: Reusable loading indicator
- **...**: Additional shared components

### Context
- **AppContext.tsx**: Global state management

### Hooks
- **useApiError.ts**: Error handling logic
- **useDataFetching.ts**: Data fetching with loading states

### Pages
- **DashboardPage.tsx**: Main dashboard view
- **TeamsPage.tsx**: Team directory and comparison
- **PredictionsPage.tsx**: Match prediction interface
- **UploadPage.tsx**: Data upload functionality
- **SettingsPage.tsx**: Application settings

### Services
- **api.ts**: Axios-based API client

### Types
- **index.ts**: TypeScript type definitions

### Utils
- **helpers.ts**: Utility functions

## 🔧 Configuration Options

### Environment Variables

```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1

# Build Configuration
GENERATE_SOURCEMAP=false
DISABLE_ESLINT_PLUGIN=true
```

### Theme Customization

Edit `src/index.tsx` to modify:
- Color palette
- Typography
- Component defaults
- Dark/light mode preferences

## 🚀 Deployment

### Production Build

```bash
npm run build
```

### Serving the App

The production build can be served by:
- Nginx
- Apache
- Any static file server
- The FastAPI backend (configured to serve static files)

### Docker Deployment

```dockerfile
FROM node:16 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## 📚 Documentation

- **API Documentation**: Available at `/api/docs` when backend is running
- **Component Documentation**: TypeScript types and JSDoc comments
- **Architecture**: See main README for system overview

## 🤝 Contributing

### Code Style
- Follow existing code patterns
- Use TypeScript interfaces for props
- Add JSDoc comments for complex functions
- Keep components focused and reusable

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Write tests
5. Update documentation
6. Submit pull request

## 🎯 Future Enhancements

### UI/UX Improvements
- Advanced data visualizations
- Interactive charts and graphs
- Real-time updates with WebSockets
- Mobile-responsive design enhancements

### Feature Additions
- Team scouting integration
- Match scheduling tools
- Historical performance analysis
- Export functionality (CSV, PDF)

### Technical Improvements
- State management with Redux or Zustand
- Server-side rendering (Next.js)
- Internationalization support
- Enhanced accessibility features

## 📞 Support

For issues and questions:
- Check the main README
- Review API documentation
- Open GitHub issues for bugs
- Submit feature requests

## 📝 License

MIT License - see the LICENSE file in the project root for details.