# API Key Authentication

This document describes the system-level API key authentication feature added to the Classic Models API.

## Overview

The API now supports two authentication methods:
1. **JWT Authentication** - Standard user-based authentication
2. **API Key Authentication** - System-level authentication with full admin access

API key authentication is designed for demo purposes, automated scripts, and system integrations where user-based authentication is not practical.

## Features

- ✅ **Full Admin Access** - API key grants complete read/write/delete permissions
- ✅ **Alternative Authentication** - Works as an alternative to JWT (not required alongside it)
- ✅ **Simple Implementation** - Just add `X-API-Key` header to requests
- ✅ **Environment-Based** - API key stored securely in environment variables
- ✅ **Optional** - Can be disabled by not setting the `API_KEY` environment variable
- ✅ **Well-Tested** - Comprehensive test suite included

## Configuration

### 1. Generate a Secure API Key

```bash
# Generate a secure random API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output: `xK7mP9nQ2wR5tY8uI1oL4aS6dF3gH0jK9mN2bV5cX8zA1qW4eR7tY0uI3oP6`

### 2. Set Environment Variable

Add to your `.env` file:

```bash
API_KEY=xK7mP9nQ2wR5tY8uI1oL4aS6dF3gH0jK9mN2bV5cX8zA1qW4eR7tY0uI3oP6
```

Or export in your shell:

```bash
export API_KEY="xK7mP9nQ2wR5tY8uI1oL4aS6dF3gH0jK9mN2bV5cX8zA1qW4eR7tY0uI3oP6"
```

### 3. Restart the Application

```bash
make stop
make start
```

## Usage

### Basic Request

```bash
curl -H "X-API-Key: your-api-key-here" \
  http://localhost:8000/classic-models/api/v1/products/
```

### Create a Product

```bash
curl -X POST \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "productCode": "S99_9999",
    "productName": "Test Product",
    "productLine": "Classic Cars",
    "productScale": "1:10",
    "productVendor": "Test Vendor",
    "productDescription": "A test product",
    "quantityInStock": 100,
    "buyPrice": "50.00",
    "MSRP": "75.00"
  }' \
  http://localhost:8000/classic-models/api/v1/products/
```

### Python Example

```python
import requests

API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:8000/classic-models/api/v1"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Get all products
response = requests.get(f"{BASE_URL}/products/", headers=headers)
products = response.json()

# Create a new product
new_product = {
    "productCode": "S99_9999",
    "productName": "Test Product",
    "productLine": "Classic Cars",
    "productScale": "1:10",
    "productVendor": "Test Vendor",
    "productDescription": "A test product",
    "quantityInStock": 100,
    "buyPrice": "50.00",
    "MSRP": "75.00"
}
response = requests.post(f"{BASE_URL}/products/", json=new_product, headers=headers)
```

### JavaScript Example

```javascript
const API_KEY = 'your-api-key-here';
const BASE_URL = 'http://localhost:8000/classic-models/api/v1';

// Get all products
fetch(`${BASE_URL}/products/`, {
  headers: {
    'X-API-Key': API_KEY
  }
})
  .then(response => response.json())
  .then(data => console.log(data));

// Create a new product
fetch(`${BASE_URL}/products/`, {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    productCode: 'S99_9999',
    productName: 'Test Product',
    productLine: 'Classic Cars',
    productScale: '1:10',
    productVendor: 'Test Vendor',
    productDescription: 'A test product',
    quantityInStock: 100,
    buyPrice: '50.00',
    MSRP: '75.00'
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## How It Works

### Authentication Flow

1. **Request arrives** with `X-API-Key` header
2. **ApiKeyAuthentication** class checks the header
3. If API key matches environment variable, returns **SystemUser**
4. **SystemUser** has full admin privileges (is_staff=True, is_superuser=True)
5. Request proceeds with full access

### SystemUser Class

The `SystemUser` is a special user object that:
- Is not stored in the database
- Has `is_authenticated = True`
- Has `is_staff = True`
- Has `is_superuser = True`
- Has username `"system_api_key"`

### Authentication Priority

The API tries authentication methods in this order:
1. **API Key** (if `X-API-Key` header present)
2. **JWT Token** (if `Authorization: Bearer` header present)

If neither is provided or both are invalid, the request is rejected with 401 Unauthorized.

## Security Considerations

### For Demo/Development

✅ **Acceptable Use Cases:**
- Local development and testing
- Demo environments
- Automated testing scripts
- Internal tools and scripts
- Proof-of-concept projects

### For Production

⚠️ **Important Considerations:**

1. **Treat API Key Like a Password**
   - Never commit to version control
   - Use environment variables
   - Rotate regularly

2. **Use HTTPS**
   - Always use HTTPS in production
   - API keys in plain HTTP can be intercepted

3. **Consider Alternatives**
   - For production, consider OAuth2, service accounts, or mTLS
   - API keys are simple but less secure than modern alternatives

4. **Monitor Usage**
   - Log API key usage
   - Set up alerts for suspicious activity
   - Implement rate limiting

5. **Disable If Not Needed**
   - Simply don't set the `API_KEY` environment variable
   - API key authentication will be disabled

## Testing

Run the API key authentication tests:

```bash
# Run all tests
make test

# Run only API key tests
docker-compose exec web pytest tests/test_api/test_api_key_auth.py -v
```

### Test Coverage

The test suite includes:
- ✅ Successful authentication with valid API key
- ✅ Failed authentication with invalid API key
- ✅ Fallback to JWT when API key not provided
- ✅ Error when API key not configured
- ✅ Full CRUD access with API key
- ✅ Coexistence with JWT authentication
- ✅ SystemUser properties validation

## Disabling API Key Authentication

To disable API key authentication:

1. Remove or comment out `API_KEY` from `.env`:
   ```bash
   # API_KEY=your-api-key-here
   ```

2. Restart the application:
   ```bash
   make stop
   make start
   ```

3. API key authentication will be disabled, but JWT will still work

## Troubleshooting

### "Invalid API key" Error

- Check that `API_KEY` is set in your environment
- Verify the API key matches exactly (no extra spaces)
- Ensure you're using the `X-API-Key` header (case-sensitive)

### "API key authentication is not configured" Error

- The `API_KEY` environment variable is not set
- Set it in your `.env` file and restart the application

### API Key Not Working

```bash
# Check if API_KEY is set
docker-compose exec web env | grep API_KEY

# Check Django settings
docker-compose exec web python manage.py shell
>>> import os
>>> os.environ.get('API_KEY')
```

## Implementation Files

- **Authentication Class**: `authentication/api_key_auth.py`
- **Settings Configuration**: `config/settings/base.py`
- **Tests**: `tests/test_api/test_api_key_auth.py`
- **Documentation**: `README.md`, `API_KEY_AUTHENTICATION.md`

## API Documentation

The API key authentication is documented in:
- Swagger UI: http://localhost:8000/classic-models/api/docs/
- ReDoc: http://localhost:8000/classic-models/api/redoc/

Look for the "Authentication Methods" section in the API description.

## Support

For questions or issues:
1. Check this documentation
2. Review the test suite for examples
3. Check the implementation in `authentication/api_key_auth.py`