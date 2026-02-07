# FastResult Frontend - Setup Guide

## Installation

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Setup Instructions

1. **Navigate to Frontend Directory**
```bash
cd fastresult_frontend
```

2. **Install Dependencies**
```bash
npm install
```

3. **Create .env File**
```bash
cp .env.example .env.local
```

4. **Start Development Server**
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm preview

# Run linter
npm run lint

# Format code with prettier
npm run format
```

## Project Structure

```
src/
├── app/               # React app entry and providers
├── router/           # Route definitions and guards
├── layouts/          # Layout components
├── services/         # API clients
├── store/           # Redux store and slices
├── hooks/           # Custom React hooks
├── utils/           # Utility functions
├── components/      # Reusable UI components
├── modules/         # Feature modules by role
├── pages/           # Standalone pages
├── assets/          # Images and static files
└── styles/          # Global and theme styles
```

## Components Structure

### Store (Redux Slices)
- `authSlice`: Authentication state
- `userSlice`: User profile data
- `resultSlice`: Academic results
- `academicSlice`: Academic data
- `notificationSlice`: Notifications

### Services (API Clients)
- `authService`: Authentication endpoints
- `resultService`: Result management
- `academicService`: Academic data
- `reportService`: Reports and analytics
- `notificationService`: Notifications

### Hooks
- `useAuth`: Authentication state
- `useRole`: User role
- `usePermissions`: Role-based permissions

## Environment Variables

Create `.env.local`:

```
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=FastResult
```

## Development

### Starting Development Server
```bash
npm run dev
```

### Building
```bash
npm run build
```

### Code Quality
```bash
npm run lint
npm run format
```

## Modules by Role

- **universityAdmin**: University administration dashboard
- **dean**: Faculty dean oversight
- **hod**: Department head operations
- **examOfficer**: Exam management
- **lecturer**: Course and result management
- **student**: Results and transcript view
- **public**: Landing, auth, error pages

## API Integration

All API calls go through `apiClient.js` which:
- Sets base URL
- Adds authorization headers
- Handles token management
- Manages error responses

## Authentication Flow

1. User logs in → `authService.login()`
2. Token stored in localStorage
3. Token added to all API requests
4. On 401, redirect to login
5. On logout, clear token

## Styling

- Global styles: `src/styles/globals/index.css`
- Theme styles: `src/styles/themes/`
- Dashboard styles: `src/styles/dashboard/`
- Component styles: Component-level CSS/modules

## Building for Production

```bash
npm run build
```

Output will be in `dist/` directory. Deploy this folder to your web server.

## Deployment

### Static Hosting (Vercel, Netlify)
```bash
npm run build
# Deploy dist folder
```

### Self-hosted
Copy `dist/` contents to web server and configure server to route all requests to `index.html`.
