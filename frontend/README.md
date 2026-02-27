# TradeInsight Pro Frontend (Vite + React)

## Setup

```bash
cd frontend
npm install
npm run dev
```

## Environment

Copy `.env.example` to `.env` and adjust values.

## Folder Structure

```text
frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── authApi.js
│   │   ├── client.js
│   │   └── marketApi.js
│   ├── components/
│   │   ├── DraggersList.jsx
│   │   ├── MetricCard.jsx
│   │   ├── Navbar.jsx
│   │   ├── SectorHeatmap.jsx
│   │   └── StrengthMeter.jsx
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── layouts/
│   │   └── AppLayout.jsx
│   ├── pages/
│   │   ├── AdminPanelPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── LoginPage.jsx
│   │   ├── OptionAnalysisPage.jsx
│   │   ├── ProfilePage.jsx
│   │   ├── RegisterPage.jsx
│   │   └── SubscriptionPage.jsx
│   ├── router/
│   │   ├── AppRoutes.jsx
│   │   └── ProtectedRoute.jsx
│   ├── styles/
│   │   └── global.css
│   ├── utils/
│   │   ├── env.js
│   │   └── storage.js
│   ├── App.jsx
│   └── main.jsx
├── .env.example
├── index.html
├── package.json
└── vite.config.js
```

## Features

- Dark-theme fintech dashboard
- Responsive widgets and navigation
- Axios-based API service layer
- JWT token storage in localStorage
- Context-driven authentication and route protection
- Role-based access for Admin Panel route
