# Bond Management System - Frontend

React frontend application for the Bond Portfolio Management System built with Vite, React 18, and Material-UI.

## Features

- JWT Authentication with role-based access control
- Dashboard with portfolio statistics
- Bond purchase management
- Coupon payment calculator and history
- Reports and Excel exports
- Responsive Material-UI design
- Real-time toast notifications

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - Component library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Hook Form** - Form validation
- **Yup** - Schema validation
- **React Hot Toast** - Toast notifications
- **Date-fns** - Date utilities

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your backend API URL:
```
VITE_API_URL=http://localhost:8000/api/v1
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── api/                # API client configuration
│   └── client.js       # Axios instance with interceptors
├── components/         # React components
│   ├── auth/          # Authentication components
│   ├── bonds/         # Bond management components
│   ├── common/        # Shared components (Layout, etc.)
│   ├── payments/      # Payment components
│   └── reports/       # Report components
├── contexts/          # React contexts
│   └── AuthContext.jsx # Authentication context
├── hooks/             # Custom React hooks
├── pages/             # Page components
│   ├── Dashboard.jsx  # Dashboard page
│   ├── Bonds.jsx      # Bonds page
│   ├── Login.jsx      # Login page
│   ├── Payments.jsx   # Payments page
│   └── Reports.jsx    # Reports page
├── utils/             # Utility functions
│   ├── formatters.js  # Formatting utilities
│   └── validators.js  # Validation utilities
├── App.jsx            # Main app component with routing
└── main.jsx           # Application entry point
```

## Available Routes

- `/login` - Login page
- `/dashboard` - Dashboard with portfolio statistics
- `/bonds` - Bond purchases list and creation
- `/payments` - Payment history and calculator
- `/reports` - Reports and Excel exports (Admin/Treasurer only)

## User Roles

- **Admin** - Full system access
- **Treasurer** - Manage bonds, payments, and reports
- **Member** - View own portfolio and payments

## Authentication

The app uses JWT tokens for authentication. Tokens are stored in localStorage and automatically included in API requests via Axios interceptors.

## Key Components

### Dashboard
- Portfolio summary cards
- Total investment, current value, returns
- Active bonds count

### Bond Management
- Create new bond purchases (Admin/Treasurer)
- View all bond purchases
- Automatic face value and price calculations

### Payment Processing
- Coupon payment calculator
- Payment history table
- Process payments for date ranges

### Reports
- Export monthly summaries to Excel
- Export payment registers
- Download formatted Excel files

## Environment Variables

- `VITE_API_URL` - Backend API base URL (default: http://localhost:8000/api/v1)

## Default Login Credentials

Use the credentials configured in your backend:
- Username: `admin`
- Password: `admin123`

## Contributing

This is a private project for a Cooperative Society.

## License

Proprietary - All rights reserved by the Cooperative Society.
