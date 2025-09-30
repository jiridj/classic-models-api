# Classic Models API Tests

This directory contains comprehensive unit tests for the Classic Models API project.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and shared fixtures
├── test_settings.py           # Django test settings
├── pytest.ini                # Pytest configuration
├── test_utils.py              # Test utilities and helper functions
├── test_models/               # Model tests
│   ├── __init__.py
│   ├── test_product_line.py
│   ├── test_product.py
│   ├── test_office.py
│   ├── test_employee.py
│   ├── test_customer.py
│   ├── test_order.py
│   ├── test_payment.py
│   └── test_order_detail.py
└── test_api/                  # API endpoint tests
    ├── __init__.py
    ├── test_authentication.py
    ├── test_product_line_api.py
    ├── test_product_api.py
    ├── test_office_api.py
    ├── test_employee_api.py
    ├── test_customer_api.py
    ├── test_order_api.py
    ├── test_payment_api.py
    └── test_order_detail_api.py
```

## Running Tests

### Prerequisites

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

### Running All Tests

```bash
# Using pytest (recommended)
pytest

# Using Django's test runner
python manage.py test

# Using pytest with specific options
pytest -v --tb=short
```

### Running Specific Test Categories

```bash
# Run only model tests
pytest tests/test_models/

# Run only API tests
pytest tests/test_api/

# Run only authentication tests
pytest -k "authentication"

# Run tests with specific markers
pytest -m "not slow"
pytest -m "unit"
pytest -m "api"
```

### Running Individual Test Files

```bash
# Run specific test file
pytest tests/test_models/test_product.py

# Run specific test class
pytest tests/test_models/test_product.py::TestProductModel

# Run specific test method
pytest tests/test_models/test_product.py::TestProductModel::test_product_creation
```

### Running Tests with Coverage

```bash
# Install coverage if not already installed
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML coverage report
```

## Test Configuration

### Pytest Configuration

The `pytest.ini` file contains pytest-specific configuration:

- **DJANGO_SETTINGS_MODULE**: Points to test settings
- **python_files**: Test file patterns
- **python_classes**: Test class patterns
- **python_functions**: Test function patterns
- **addopts**: Default command line options
- **markers**: Custom markers for test categorization

### Django Test Settings

The `test_settings.py` file contains Django settings optimized for testing:

- Uses in-memory SQLite database
- Disables migrations for faster tests
- Configures REST Framework for testing
- Sets up JWT authentication
- Configures logging for tests

## Test Categories

### Model Tests (`test_models/`)

Tests for Django models covering:

- **Field validation**: Max length, required fields, data types
- **Model relationships**: Foreign keys, many-to-many, self-referential
- **Model constraints**: Unique constraints, unique_together
- **Model methods**: String representation, custom methods
- **Data validation**: Unicode handling, edge cases
- **Model meta options**: Database table names, managed settings

### API Tests (`test_api/`)

Tests for REST API endpoints covering:

- **Authentication**: Login, logout, registration, token refresh
- **CRUD operations**: Create, read, update, delete for all resources
- **Permissions**: Authenticated vs unauthenticated access
- **Validation**: Input validation, error handling
- **Pagination**: List endpoint pagination
- **Filtering**: Search and filter capabilities
- **Serialization**: Data serialization and deserialization
- **HTTP methods**: GET, POST, PUT, PATCH, DELETE
- **Status codes**: Appropriate HTTP response codes

## Test Utilities

### Fixtures (`conftest.py`)

Pytest fixtures for common test data:

- **api_client**: Unauthenticated API client
- **authenticated_api_client**: Authenticated API client
- **user**: Test user
- **admin_user**: Admin user
- **office**: Test office
- **employee**: Test employee
- **customer**: Test customer
- **product_line**: Test product line
- **product**: Test product
- **order**: Test order
- **order_detail**: Test order detail
- **payment**: Test payment
- **sample_data**: Complete set of related test data

### Test Utilities (`test_utils.py`)

Helper classes and functions:

- **TestDataFactory**: Factory for creating test data
- **APITestCase**: Base test case with common setup
- **ModelTestMixin**: Utilities for model testing
- **APITestMixin**: Utilities for API testing
- **DataValidationMixin**: Data validation utilities
- **TestDataBuilder**: Builder pattern for complex test data

## Test Data

### Factory Pattern

The `TestDataFactory` class provides methods to create test data:

```python
# Create individual objects
user = TestDataFactory.create_user()
office = TestDataFactory.create_office()
employee = TestDataFactory.create_employee(office=office)

# Create related objects
customer = TestDataFactory.create_customer(employee=employee)
product = TestDataFactory.create_product()
order = TestDataFactory.create_order(customer=customer)
```

### Builder Pattern

The `TestDataBuilder` class allows chaining object creation:

```python
# Create a complete hierarchy
data = (TestDataBuilder()
        .with_user()
        .with_office()
        .with_employee()
        .with_customer()
        .with_product_line()
        .with_product()
        .with_order()
        .with_order_detail()
        .with_payment()
        .build())
```

## Test Markers

Custom pytest markers for test categorization:

- **@pytest.mark.slow**: Slow-running tests
- **@pytest.mark.integration**: Integration tests
- **@pytest.mark.unit**: Unit tests
- **@pytest.mark.api**: API tests
- **@pytest.mark.model**: Model tests
- **@pytest.mark.authentication**: Authentication tests
- **@pytest.mark.database**: Tests requiring database
- **@pytest.mark.network**: Tests requiring network
- **@pytest.mark.external**: Tests requiring external services

## Best Practices

### Test Organization

1. **One test file per model/API endpoint**
2. **Descriptive test names** that explain what is being tested
3. **Group related tests** in test classes
4. **Use fixtures** for common test data
5. **Keep tests independent** - no test should depend on another

### Test Data

1. **Use factories** for creating test data
2. **Create minimal data** needed for each test
3. **Use unique identifiers** to avoid conflicts
4. **Clean up after tests** (handled automatically by Django)

### Assertions

1. **Use specific assertions** rather than generic ones
2. **Test both positive and negative cases**
3. **Test edge cases** and boundary conditions
4. **Test error conditions** and validation

### Performance

1. **Use in-memory database** for faster tests
2. **Disable migrations** during tests
3. **Use transactions** for test isolation
4. **Minimize database queries** in tests

## Continuous Integration

### GitHub Actions

Example workflow for running tests:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Local Development

```bash
# Run tests before committing
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m "not slow"
pytest -m "unit"
```

## Troubleshooting

### Common Issues

1. **Database errors**: Ensure test database is properly configured
2. **Import errors**: Check that all dependencies are installed
3. **Authentication errors**: Verify JWT configuration
4. **Permission errors**: Check test user permissions

### Debug Mode

```bash
# Run tests with verbose output
pytest -v -s

# Run tests with debug output
pytest --pdb

# Run specific test with debug
pytest -k "test_name" --pdb
```

### Test Database

```bash
# Reset test database
python manage.py test --keepdb

# Create test database manually
python manage.py migrate --run-syncdb
```

## Contributing

When adding new tests:

1. **Follow naming conventions**: `test_<functionality>`
2. **Use descriptive names**: Explain what is being tested
3. **Add appropriate markers**: Categorize tests properly
4. **Update documentation**: Keep this README current
5. **Test edge cases**: Cover boundary conditions
6. **Test error conditions**: Verify proper error handling

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Pytest Django Plugin](https://pytest-django.readthedocs.io/)
