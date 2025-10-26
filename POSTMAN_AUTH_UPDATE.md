# Postman Collection Auth Update

## Summary

Updated the Classic Models API Postman collection to correctly use authentication headers for all requests that require authentication.

## Changes Made

### 1. Collection-Level Authentication
The collection already had Bearer token authentication configured at the collection level:
- **Type**: Bearer Token
- **Token Variable**: `{{access_token}}`

### 2. Request-Level Authentication Configuration

#### Endpoints with NO Authentication (`noauth`)
The following endpoints do not require authentication:
- **Health Check**
  - API Documentation (`/api/docs/`)
  - API Schema (`/api/schema/`)
- **Authentication**
  - Register User (`/api/auth/register/`)
  - Login User (`/api/auth/login/`)
  - Refresh Token (`/api/auth/refresh/`)
- **Documentation**
  - ReDoc (`/api/redoc/`)

#### Endpoints that INHERIT Collection Authentication (`inherit`)
The following endpoints now inherit the Bearer token authentication from the collection:
- **Authentication**
  - Get Current User (`/api/auth/me/`)
  - Logout User (`/api/auth/logout/`)
- **Product Lines** (all 6 CRUD endpoints) - `/api/v1/productlines/`
- **Products** (all 7 endpoints including search) - `/api/v1/products/`
- **Offices** (all 6 CRUD endpoints) - `/api/v1/offices/`
- **Employees** (all 6 CRUD endpoints) - `/api/v1/employees/`
- **Customers** (all 6 CRUD endpoints) - `/api/v1/customers/`
- **Orders** (all 6 CRUD endpoints) - `/api/v1/orders/`
- **Order Details** (all 6 CRUD endpoints) - `/api/v1/orderdetails/`
- **Payments** (all 6 CRUD endpoints) - `/api/v1/payments/`

### 3. Automatic Token Management

#### Login Endpoint
Automatically saves tokens to collection variables on successful login:
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.collectionVariables.set('access_token', response.access);
    pm.collectionVariables.set('refresh_token', response.refresh);
}
```

#### Refresh Token Endpoint
Automatically updates the access token on successful refresh:
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.collectionVariables.set('access_token', response.access);
}
```

## How to Use

### Step 1: Import the Collection
1. Open Postman
2. Import `Classic_Models_API.postman_collection.json`

### Step 2: Select Environment
Choose either:
- `Classic_Models_API_Local.postman_environment.json` (for local development)
- `Classic_Models_API_AWS.postman_environment.json` (for AWS/production)

### Step 3: Authenticate
1. **Register a User** (if needed):
   - Run the "Register User" request under Authentication folder
   
2. **Login**:
   - Run the "Login User" request
   - Access and refresh tokens will be automatically saved to collection variables
   
3. **Make Authenticated Requests**:
   - All CRUD endpoints will now automatically use the saved access token
   - The Bearer token is sent in the `Authorization` header as: `Bearer {{access_token}}`

### Step 4: Refresh Token (when needed)
When your access token expires:
1. Run the "Refresh Token" request
2. The new access token will be automatically saved

## Technical Details

### Backend Authentication Requirements
The API uses JWT (JSON Web Token) authentication:
- **Login endpoint** (`/api/auth/login/`) returns:
  - `access` token (short-lived)
  - `refresh` token (long-lived)
  - `user` object with user details

- **Protected endpoints** require:
  - `Authorization: Bearer <access_token>` header
  - Implemented via `permission_classes = [permissions.IsAuthenticated]`

### Token Flow
1. User logs in → receives access + refresh tokens
2. Access token used for API requests
3. When access token expires → use refresh token to get new access token
4. All authenticated requests automatically include: `Authorization: Bearer <access_token>`

## Verification

To verify the auth configuration is working:

1. **Without Auth**: Try "List Products" without logging in first
   - Expected: 401 Unauthorized

2. **With Auth**: 
   - Login using "Login User" request
   - Try "List Products" again
   - Expected: 200 OK with product data

## Variables

### Environment Variables
Both environment files include only:
- `base_url`: API base URL (environment-specific)

**Local Environment**:
```
base_url: http://localhost:8000/classic-models
```

**AWS Environment**:
```
base_url: https://dynamic-router.onrender.com/classic-models
```

### Collection Variables
The collection includes:
- `base_url`: Default base URL (can be overridden by environment)
- `access_token`: JWT access token (auto-populated on login)
- `refresh_token`: JWT refresh token (auto-populated on login)

**Note**: Authentication tokens are stored at the collection level, not in environments. This ensures tokens persist across environment switches and are managed centrally by the collection.

