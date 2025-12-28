# POS System Frontend

Next.js frontend for the Multi-Store POS, Inventory, and Accounting Platform.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Query** - Data fetching and caching
- **Zustand** - State management
- **React Hook Form** - Form handling
- **Zod** - Schema validation
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Django backend running on `http://127.0.0.1:8000`

### Installation

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create `.env.local` file:
```bash
cp .env.example .env.local
```

4. Update `.env.local` with your API URL:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

5. Run development server:
```bash
npm run dev
# or
yarn dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── dashboard/         # Dashboard pages
│   ├── inventory/         # Inventory management
│   ├── pos/               # Point of Sale interface
│   ├── transfers/         # Transfer management
│   ├── accounting/        # Accounting pages
│   ├── analytics/         # Analytics & reports
│   └── notifications/     # Notifications
├── components/            # React components
│   ├── layout/           # Layout components
│   ├── ui/               # Reusable UI components
│   └── forms/            # Form components
├── lib/                   # Utilities and helpers
│   ├── api/              # API client and types
│   ├── store/            # Zustand stores
│   └── utils.ts          # Utility functions
└── public/               # Static assets
```

## Features

- ✅ JWT Authentication
- ✅ Multi-tenant support
- ✅ Role-based UI rendering
- ✅ Responsive design
- ✅ Real-time data fetching
- ✅ Form validation
- ✅ Error handling

## API Integration

The frontend communicates with the Django backend via REST API. All API calls are handled through:
- `lib/api/client.ts` - Axios instance with interceptors
- `lib/api/auth.ts` - Authentication API
- React Query hooks for data fetching

## Authentication Flow

1. User logs in via `/login`
2. JWT tokens stored in localStorage
3. Tokens automatically added to API requests
4. Token refresh handled automatically
5. Protected routes redirect to login if not authenticated

## Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint
npm run lint
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Django API base URL

## Next Steps

- Complete all page components
- Add more UI components
- Implement offline mode
- Add real-time updates
- Enhance error handling
- Add loading states
- Implement search and filters

