# Frontend UI Architecture Blueprint (Derived from Backend Modules)

## 1) Global Frontend Architecture

### App shells
- **Public shell**: Login/Register/Forgot-password-ready routes.
- **Authenticated shell**: Main app layout with top nav, left nav, and role-based menu.
- **Admin shell**: Extends authenticated shell; includes admin-only navigation and dashboards.

### Cross-cutting frontend services
- **API client layer**
  - Axios/fetch wrapper with base URL `/api/v1`.
  - Bearer token injector and refresh-token retry flow (`/auth/refresh`).
  - Standardized error mapper (`401`, `403`, `422`, `500`, network).
- **Auth state manager**
  - Stores `access_token`, `refresh_token`, and `currentUser` (`/users/me`).
  - Guards routes by role: `free`, `pro`, `admin`.
- **Design system primitives**
  - DataTable, KPICard, EmptyState, ErrorState, LoadingSkeleton, Pagination, Toasts, ConfirmDialog.
- **Global state buckets**
  - `auth`, `userProfile`, `market`, `options`, `aiSignal`, `subscription`, `admin`.

### Standard screen-state contract (used for all pages)
Each feature page should expose these UI states:
1. **Loading**: Initial spinner/skeleton + disabled actions.
2. **Error**: Error block with retry, plus toast.
3. **Empty**: Informative blank-state with CTA.
4. **Success**: Data-rendered state.

---

## 2) Feature-by-Feature UI Mapping Plan

## Feature: Auth Module

### A. Backend feature: Register (`POST /auth/register`)
- **Required page**: `/register`
- **Required widgets**:
  - Registration form (email, password, full name)
  - Password strength indicator
  - Submit button + inline validation messages
  - Success redirect banner (to login or app)
- **Required API calls**:
  - `POST /api/v1/auth/register`
- **Required user role**:
  - Public (unauthenticated)
- **Required states**:
  - Loading: submit button spinner
  - Error: field-level + form-level API errors
  - Empty: not applicable (form page)

### B. Backend feature: Login (`POST /auth/login`)
- **Required page**: `/login`
- **Required widgets**:
  - Login form (email, password)
  - Remember me (optional frontend only)
  - Submit CTA
  - Link to register
- **Required API calls**:
  - `POST /api/v1/auth/login`
  - `GET /api/v1/users/me` (immediately after login)
- **Required user role**:
  - Public
- **Required states**:
  - Loading: login in progress
  - Error: invalid credentials/auth failure
  - Empty: not applicable

### C. Backend feature: Refresh token (`POST /auth/refresh`)
- **Required page**: none (background infrastructure)
- **Required widgets**:
  - None visible; session expiry modal optional
- **Required API calls**:
  - `POST /api/v1/auth/refresh`
- **Required user role**:
  - Authenticated session with refresh token
- **Required states**:
  - Loading: silent request
  - Error: force logout + redirect to `/login`
  - Empty: not applicable

---

## Feature: Users Module

### D. Backend feature: Current profile (`GET /users/me`)
- **Required page**: `/profile`
- **Required widgets**:
  - Profile summary card (email, full name, role, telegram, created date)
  - Role badge (`FREE`, `PRO`, `ADMIN`)
- **Required API calls**:
  - `GET /api/v1/users/me`
- **Required user role**:
  - `free | pro | admin`
- **Required states**:
  - Loading: profile skeleton
  - Error: auth/session/user fetch failed
  - Empty: no profile data fallback (rare)

### E. Backend feature: Link Telegram (`PUT /users/me/telegram-link`)
- **Required page**: `/profile` (section: Integrations)
- **Required widgets**:
  - Telegram ID input
  - Save/update button
  - Validation helper text
- **Required API calls**:
  - `PUT /api/v1/users/me/telegram-link`
  - `GET /api/v1/users/me` (refresh profile)
- **Required user role**:
  - `free | pro | admin`
- **Required states**:
  - Loading: button spinner + disable form
  - Error: invalid/duplicate telegram id
  - Empty: telegram not linked state with CTA

---

## Feature: Nifty Market Module

### F. Backend feature: Latest Nifty snapshot (`GET /nifty/latest`)
- **Required page**: `/dashboard` (market overview)
- **Required widgets**:
  - Nifty index live card (price, timestamp)
  - Last-updated indicator
- **Required API calls**:
  - `GET /api/v1/nifty/latest`
- **Required user role**:
  - `free | pro | admin`
- **Required states**:
  - Loading: KPI skeleton
  - Error: unavailable market snapshot
  - Empty: no snapshot message + retry

### G. Backend feature: Nifty impact analytics (`GET /nifty/impact`)
- **Required page**: `/nifty-impact`
- **Required widgets**:
  - Total impact KPI
  - Top draggers table
  - Constituents impact sortable table
- **Required API calls**:
  - `GET /api/v1/nifty/impact`
- **Required user role**:
  - `free | pro | admin`
- **Required states**:
  - Loading: table skeleton + KPI placeholders
  - Error: analytics fetch failed
  - Empty: no constituent data

### H. Backend feature: Sector heatmap (`GET /nifty/impact/sector-heatmap`)
- **Required page**: `/nifty-impact` (tab: Sector Heatmap)
- **Required widgets**:
  - Heatmap grid (sector -> impact)
  - Color legend
  - Tooltip on hover
- **Required API calls**:
  - `GET /api/v1/nifty/impact/sector-heatmap`
- **Required user role**:
  - `free | pro | admin`
- **Required states**:
  - Loading: heatmap skeleton
  - Error: heatmap load error
  - Empty: no sectors available

---

## Feature: Options Module

### I. Backend feature: Latest options contracts (`GET /options/latest`)
- **Required page**: `/options/latest`
- **Required widgets**:
  - Contracts table (symbol, strike, premium, type, updated_at)
  - Limit selector (1..100)
  - Pro lock badge for unauthorized roles
- **Required API calls**:
  - `GET /api/v1/options/latest?limit={n}`
- **Required user role**:
  - `pro | admin`
- **Required states**:
  - Loading: table skeleton
  - Error: forbidden (403) or server error
  - Empty: no option contracts

### J. Backend feature: Option chain analytics (`GET /options/analytics`)
- **Required page**: `/options/analytics`
- **Required widgets**:
  - Filters: symbol, expiry date
  - KPI panel: PCR, OI totals, change OI PCR
  - Support/resistance/max pain cards
  - Timestamp and underlying value display
- **Required API calls**:
  - `GET /api/v1/options/analytics?symbol={symbol}&expiry_date={date}`
- **Required user role**:
  - `free | pro | admin`
- **Required states**:
  - Loading: KPI skeleton blocks
  - Error: analytics unavailable/invalid params
  - Empty: no chain available for selected expiry

---

## Feature: AI Signal Module

### K. Backend feature: Latest AI signal (`GET /ai-signal/latest`)
- **Required page**: `/ai-signal`
- **Required widgets**:
  - Signal score gauge (0-100)
  - Classification badge (Bullish/Bearish/Neutral style)
  - Timestamped refresh CTA
  - Pro entitlement prompt
- **Required API calls**:
  - `GET /api/v1/ai-signal/latest`
- **Required user role**:
  - `pro | admin`
- **Required states**:
  - Loading: gauge placeholder
  - Error: 403 access denied or service failure
  - Empty: no signal generated yet

---

## Feature: Subscription Module

### L. Backend feature: Create order (`POST /subscription/create-order`)
- **Required page**: `/pricing` and `/checkout`
- **Required widgets**:
  - Plan card(s)
  - Amount summary
  - Pay button (Razorpay launcher)
- **Required API calls**:
  - `POST /api/v1/subscription/create-order`
- **Required user role**:
  - `free | pro | admin` (practically free users upgrading)
- **Required states**:
  - Loading: checkout initiation spinner
  - Error: order creation/payment init failure
  - Empty: no active plans configured

### M. Backend feature: Verify payment (`POST /subscription/verify-payment`)
- **Required page**: `/checkout/result`
- **Required widgets**:
  - Payment processing modal
  - Success/failure result card
  - CTA to go to pro features
- **Required API calls**:
  - `POST /api/v1/subscription/verify-payment`
  - `GET /api/v1/users/me` (role refresh after success)
- **Required user role**:
  - `free | pro | admin`
- **Required states**:
  - Loading: verification in progress
  - Error: signature/payment verification failed
  - Empty: no payment context (direct route hit)

### N. Backend feature: Webhook (`POST /subscription/webhook`)
- **Required page**: none (backend-only callback)
- **Required widgets**: none
- **Required API calls**:
  - No direct frontend call required
- **Required user role**:
  - Public endpoint (system-to-system)
- **Required states**:
  - Not applicable in UI

---

## Feature: Admin Module

### O. Backend feature: List users (`GET /admin/users`)
- **Required page**: `/admin/users`
- **Required widgets**:
  - Paginated users table
  - Search/filter controls (frontend filter optional)
  - Role chip and actions column
- **Required API calls**:
  - `GET /api/v1/admin/users?page={p}&size={s}`
- **Required user role**:
  - `admin`
- **Required states**:
  - Loading: admin table skeleton
  - Error: unauthorized/admin fetch error
  - Empty: no users

### P. Backend feature: Update user role (`PATCH /admin/users/{user_id}/role`)
- **Required page**: `/admin/users` (inline action)
- **Required widgets**:
  - Role dropdown/select in row
  - Confirmation modal
  - Success/error toast
- **Required API calls**:
  - `PATCH /api/v1/admin/users/{user_id}/role`
  - `GET /api/v1/admin/users` (refresh current page)
- **Required user role**:
  - `admin`
- **Required states**:
  - Loading: row-level action loader
  - Error: update rejected/conflict
  - Empty: not applicable

### Q. Backend feature: List subscriptions (`GET /admin/subscriptions`)
- **Required page**: `/admin/subscriptions`
- **Required widgets**:
  - Paginated subscriptions table
  - Status badges (`pending`, `active`, `failed`, etc.)
  - Expiry and payment ID columns
- **Required API calls**:
  - `GET /api/v1/admin/subscriptions?page={p}&size={s}`
- **Required user role**:
  - `admin`
- **Required states**:
  - Loading: table skeleton
  - Error: fetch failed
  - Empty: no subscriptions

### R. Backend feature: API usage logs (`GET /admin/api-usage-logs`)
- **Required page**: `/admin/api-logs`
- **Required widgets**:
  - Paginated logs table
  - Method/status filters
  - Timestamp and path columns
- **Required API calls**:
  - `GET /api/v1/admin/api-usage-logs?page={p}&size={s}`
- **Required user role**:
  - `admin`
- **Required states**:
  - Loading: log table skeleton
  - Error: fetch failed
  - Empty: no logs

### S. Backend feature: List feature flags (`GET /admin/feature-flags`)
- **Required page**: `/admin/feature-flags`
- **Required widgets**:
  - Paginated flags table
  - Toggle switch per flag
  - Updated timestamp display
- **Required API calls**:
  - `GET /api/v1/admin/feature-flags?page={p}&size={s}`
- **Required user role**:
  - `admin`
- **Required states**:
  - Loading: flags skeleton
  - Error: fetch failed
  - Empty: no flags configured

### T. Backend feature: Toggle feature flag (`PATCH /admin/feature-flags/{name}`)
- **Required page**: `/admin/feature-flags` (inline toggle action)
- **Required widgets**:
  - Toggle switch
  - Confirm action popover (recommended)
  - Save indicator (optimistic update or rollback)
- **Required API calls**:
  - `PATCH /api/v1/admin/feature-flags/{name}`
  - `GET /api/v1/admin/feature-flags` (optional sync refresh)
- **Required user role**:
  - `admin`
- **Required states**:
  - Loading: per-toggle spinner
  - Error: revert toggle + toast
  - Empty: not applicable

---

## Feature: Protected Role-Demo Module

### U. Backend feature: Protected free/pro/admin demo routes
- **Required page**: `/access-check` (diagnostic page for QA)
- **Required widgets**:
  - Three call buttons: Free, Pro, Admin check
  - Response panel showing message or access denied
- **Required API calls**:
  - `GET /api/v1/protected/free`
  - `GET /api/v1/protected/pro`
  - `GET /api/v1/protected/admin`
- **Required user role**:
  - Per endpoint role gate
- **Required states**:
  - Loading: request spinner per button
  - Error: forbidden/unauthorized diagnostics
  - Empty: no request made yet

---

## 3) Route Map (Recommended)

### Public routes
- `/login`
- `/register`
- `/pricing`

### Authenticated routes (`free | pro | admin` unless noted)
- `/dashboard`
- `/profile`
- `/nifty-impact`
- `/options/analytics`
- `/checkout`
- `/checkout/result`
- `/access-check`

### Pro routes
- `/options/latest`
- `/ai-signal`

### Admin routes
- `/admin/users`
- `/admin/subscriptions`
- `/admin/api-logs`
- `/admin/feature-flags`

---

## 4) Role-Based Navigation Blueprint

- **Free user nav**: Dashboard, Nifty Impact, Options Analytics, Profile, Pricing.
- **Pro user nav**: Free nav + Options Latest + AI Signal.
- **Admin user nav**: Pro nav + Admin dropdown (Users, Subscriptions, API Logs, Feature Flags).

---

## 5) API Integration Inventory (Frontend Service Contracts)

- `authApi.register(payload)` -> `POST /auth/register`
- `authApi.login(payload)` -> `POST /auth/login`
- `authApi.refresh(payload)` -> `POST /auth/refresh`
- `userApi.getMe()` -> `GET /users/me`
- `userApi.linkTelegram(payload)` -> `PUT /users/me/telegram-link`
- `niftyApi.getLatest()` -> `GET /nifty/latest`
- `niftyApi.getImpact()` -> `GET /nifty/impact`
- `niftyApi.getSectorHeatmap()` -> `GET /nifty/impact/sector-heatmap`
- `optionsApi.getLatest(limit)` -> `GET /options/latest`
- `optionsApi.getAnalytics(params)` -> `GET /options/analytics`
- `aiSignalApi.getLatest()` -> `GET /ai-signal/latest`
- `subscriptionApi.createOrder(payload)` -> `POST /subscription/create-order`
- `subscriptionApi.verifyPayment(payload)` -> `POST /subscription/verify-payment`
- `adminApi.listUsers(params)` -> `GET /admin/users`
- `adminApi.updateUserRole(userId, payload)` -> `PATCH /admin/users/{user_id}/role`
- `adminApi.listSubscriptions(params)` -> `GET /admin/subscriptions`
- `adminApi.listApiUsageLogs(params)` -> `GET /admin/api-usage-logs`
- `adminApi.listFeatureFlags(params)` -> `GET /admin/feature-flags`
- `adminApi.toggleFeatureFlag(name, payload)` -> `PATCH /admin/feature-flags/{name}`
- `debugApi.checkFree()` -> `GET /protected/free`
- `debugApi.checkPro()` -> `GET /protected/pro`
- `debugApi.checkAdmin()` -> `GET /protected/admin`

---

## 6) Implementation Priority (Suggested)

1. **Auth + Session foundation** (login/register/refresh/me + route guards)
2. **Core user pages** (dashboard/profile/telegram)
3. **Market intelligence pages** (nifty impact + options analytics)
4. **Monetization path** (pricing + checkout + verify)
5. **Pro value pages** (options latest + AI signal)
6. **Admin console** (users/subscriptions/logs/flags)
7. **Diagnostic access-check page**

This blueprint is complete against currently exposed backend modules and API routes.
