# FastAPI API Contract (v1)

Base prefix: `/api/v1`

## Auth

### 1) `POST /api/v1/auth/register`
- **Request schema (`UserCreate`)**
  - `email: EmailStr`
  - `password: str` (min 8, max 128)
  - `full_name: str | null`
- **Response schema (`UserRead`)**
  - `id: int`
  - `email: EmailStr`
  - `full_name: str | null`
  - `telegram_id: str | null`
  - `role: UserRole`
  - `is_active: bool`
  - `created_at: datetime`
- **Required role**: Public (no role required)

### 2) `POST /api/v1/auth/login`
- **Request schema (`LoginRequest`)**
  - `email: EmailStr`
  - `password: str` (min 8, max 128)
- **Response schema (`Token`)**
  - `access_token: str`
  - `refresh_token: str`
  - `token_type: str` (default `bearer`)
- **Required role**: Public (no role required)

### 3) `POST /api/v1/auth/refresh`
- **Request schema (`RefreshTokenRequest`)**
  - `refresh_token: str`
- **Response schema (`Token`)**
  - `access_token: str`
  - `refresh_token: str`
  - `token_type: str` (default `bearer`)
- **Required role**: Public (no role required)

## Users

### 4) `GET /api/v1/users/me`
- **Request schema**: No body (Bearer auth required)
- **Response schema (`UserRead`)**
  - `id: int`
  - `email: EmailStr`
  - `full_name: str | null`
  - `telegram_id: str | null`
  - `role: UserRole`
  - `is_active: bool`
  - `created_at: datetime`
- **Required role**: Any authenticated user (`free | pro | admin`)

### 5) `PUT /api/v1/users/me/telegram-link`
- **Request schema (`TelegramLinkRequest`)**
  - `telegram_id: str` (min 1, max 64)
- **Response schema (`UserRead`)**
  - `id: int`
  - `email: EmailStr`
  - `full_name: str | null`
  - `telegram_id: str | null`
  - `role: UserRole`
  - `is_active: bool`
  - `created_at: datetime`
- **Required role**: Any authenticated user (`free | pro | admin`)

## Nifty

### 6) `GET /api/v1/nifty/latest`
- **Request schema**: No body (Bearer auth required)
- **Response schema (`NiftySnapshotRead`)**
  - `id: int`
  - `symbol: str`
  - `price: float`
  - `captured_at: datetime`
- **Required role**: Any authenticated user (`free | pro | admin`)

### 7) `GET /api/v1/nifty/impact`
- **Request schema**: No body (Bearer auth required)
- **Response schema (`NiftyImpactResponse`)**
  - `index: str`
  - `total_impact: float`
  - `top_draggers: NiftyConstituentImpact[]`
    - `symbol: str`
    - `company_name: str`
    - `weight: float`
    - `last_price: float`
    - `percent_change: float`
    - `impact: float`
  - `constituents: NiftyConstituentImpact[]` (same fields)
- **Required role**: Any authenticated user (`free | pro | admin`)

### 8) `GET /api/v1/nifty/impact/sector-heatmap`
- **Request schema**: No body (Bearer auth required)
- **Response schema (`SectorImpactHeatmapResponse`)**
  - Root object: `dict[str, float]`
- **Required role**: Any authenticated user (`free | pro | admin`)

## Options

### 9) `GET /api/v1/options/latest`
- **Request schema**
  - Query param: `limit: int = 20` (`1 <= limit <= 100`)
  - No body
- **Response schema (`OptionContractRead[]`)**
  - `id: int`
  - `symbol: str`
  - `strike_price: float`
  - `premium: float`
  - `option_type: str`
  - `updated_at: datetime | null`
- **Required role**: `pro | admin`

### 10) `GET /api/v1/options/analytics`
- **Request schema**
  - Query param: `symbol: str = "NIFTY"` (min 1, max 30)
  - Query param: `expiry_date: str | null`
  - No body
- **Response schema (`OptionsAnalyticsResponse`)**
  - `symbol: str`
  - `expiry_date: str`
  - `underlying_value: float | null`
  - `timestamp: datetime`
  - `total_call_oi: int`
  - `total_put_oi: int`
  - `pcr: float | null`
  - `change_in_call_oi: int`
  - `change_in_put_oi: int`
  - `change_oi_pcr: float | null`
  - `strongest_support: float | null`
  - `strongest_resistance: float | null`
  - `max_pain: float | null`
- **Required role**: Any authenticated user (`free | pro | admin`)

## AI Signal

### 11) `GET /api/v1/ai-signal/latest`
- **Request schema**: No body (Bearer auth required)
- **Response schema (`AISignalEngineResponse`)**
  - `score: int`
  - `classification: str`
- **Required role**: `pro | admin`

## Admin

### 12) `GET /api/v1/admin/users`
- **Request schema**
  - Query param: `page: int = 1` (>=1)
  - Query param: `size: int = 20` (1..100)
  - No body
- **Response schema (`PaginatedUsersResponse`)**
  - `items: UserRead[]`
  - `total: int`
  - `page: int`
  - `size: int`
- **Required role**: `admin`

### 13) `PATCH /api/v1/admin/users/{user_id}/role`
- **Request schema**
  - Path param: `user_id: int` (>=1)
  - Body (`UserRoleUpdate`):
    - `role: UserRole`
- **Response schema (`UserRead`)**
  - `id: int`
  - `email: EmailStr`
  - `full_name: str | null`
  - `telegram_id: str | null`
  - `role: UserRole`
  - `is_active: bool`
  - `created_at: datetime`
- **Required role**: `admin`

### 14) `GET /api/v1/admin/subscriptions`
- **Request schema**
  - Query param: `page: int = 1` (>=1)
  - Query param: `size: int = 20` (1..100)
  - No body
- **Response schema (`PaginatedSubscriptionsResponse`)**
  - `items: SubscriptionAdminRead[]`
    - `id: int`
    - `user_id: int`
    - `user_email: str`
    - `status: SubscriptionStatus`
    - `razorpay_order_id: str`
    - `razorpay_payment_id: str | null`
    - `expiry_date: datetime | null`
    - `created_at: datetime`
  - `total: int`
  - `page: int`
  - `size: int`
- **Required role**: `admin`

### 15) `GET /api/v1/admin/api-usage-logs`
- **Request schema**
  - Query param: `page: int = 1` (>=1)
  - Query param: `size: int = 20` (1..100)
  - No body
- **Response schema (`PaginatedAPIUsageLogsResponse`)**
  - `items: APIUsageLogRead[]`
    - `id: int`
    - `user_id: int | null`
    - `method: str`
    - `path: str`
    - `status_code: int`
    - `ip_address: str | null`
    - `created_at: datetime`
  - `total: int`
  - `page: int`
  - `size: int`
- **Required role**: `admin`

### 16) `GET /api/v1/admin/feature-flags`
- **Request schema**
  - Query param: `page: int = 1` (>=1)
  - Query param: `size: int = 20` (1..100)
  - No body
- **Response schema (`PaginatedFeatureFlagsResponse`)**
  - `items: FeatureFlagRead[]`
    - `id: int`
    - `name: str`
    - `enabled: bool`
    - `updated_at: datetime`
  - `total: int`
  - `page: int`
  - `size: int`
- **Required role**: `admin`

### 17) `PATCH /api/v1/admin/feature-flags/{name}`
- **Request schema**
  - Path param: `name: str`
  - Body (`FeatureFlagToggleRequest`):
    - `enabled: bool`
- **Response schema (`FeatureFlagRead`)**
  - `id: int`
  - `name: str`
  - `enabled: bool`
  - `updated_at: datetime`
- **Required role**: `admin`

## Protected (role examples)

### 18) `GET /api/v1/protected/free`
- **Request schema**: No body
- **Response schema**: `{"message": "string"}`
- **Required role**: `free | pro | admin`

### 19) `GET /api/v1/protected/pro`
- **Request schema**: No body
- **Response schema**: `{"message": "string"}`
- **Required role**: `pro | admin`

### 20) `GET /api/v1/protected/admin`
- **Request schema**: No body
- **Response schema**: `{"message": "string"}`
- **Required role**: `admin`

## Subscription

### 21) `POST /api/v1/subscription/create-order`
- **Request schema (`SubscriptionOrderCreateRequest`)**
  - `amount: int` (>0)
  - `currency: "INR"` (default)
- **Response schema (`SubscriptionOrderCreateResponse`)**
  - `order_id: str`
  - `amount: int`
  - `currency: str`
  - `key_id: str`
- **Required role**: Any authenticated user (`free | pro | admin`)

### 22) `POST /api/v1/subscription/verify-payment`
- **Request schema (`PaymentVerifyRequest`)**
  - `razorpay_order_id: str`
  - `razorpay_payment_id: str`
  - `razorpay_signature: str`
- **Response schema**: `{"message": "Payment verified successfully"}`
- **Required role**: Any authenticated user (`free | pro | admin`)

### 23) `POST /api/v1/subscription/webhook`
- **Request schema**
  - Headers: `x-razorpay-signature` (optional)
  - Raw webhook JSON body (validated internally; no public response_model)
- **Response schema**: `{"message": "Webhook accepted"}` or 400 on invalid JSON payload
- **Required role**: Public (webhook endpoint; no user auth)
- **Notes**: `include_in_schema=False` (not shown in generated OpenAPI docs, but route exists)
