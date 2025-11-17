"""
Pytest configuration and shared fixtures for the Classic Models API tests.
"""

import pytest

# Configure pytest-django to allow database access by default
pytest_plugins = ["pytest_django"]

# Allow database access for all tests by default
# pytestmark = pytest.mark.django_db  # This doesn't seem to work properly


# Remove pytest_configure - we'll handle model configuration in fixtures


@pytest.fixture(autouse=True, scope="session")
def django_setup(django_db_setup, django_db_blocker):
    """Set up Django models for testing."""
    with django_db_blocker.unblock():
        from classicmodels.models import (
            Customer,
            Employee,
            Office,
            Order,
            Orderdetail,
            Payment,
            Product,
            ProductLine,
        )

        # Override models to be managed for testing
        Office._meta.managed = True
        ProductLine._meta.managed = True
        Product._meta.managed = True
        Employee._meta.managed = True
        Customer._meta.managed = True
        Order._meta.managed = True
        Orderdetail._meta.managed = True
        Payment._meta.managed = True

        # Create database tables
        from django.db import connection

        # Create tables for all models
        with connection.schema_editor() as schema_editor:
            for model in [
                Office,
                ProductLine,
                Product,
                Employee,
                Customer,
                Order,
                Orderdetail,
                Payment,
            ]:
                schema_editor.create_model(model)


@pytest.fixture(autouse=True, scope="session")
def disable_throttling(django_setup):
    """Disable throttling for all tests by patching throttle classes."""
    # Replace throttle classes in viewsets with empty list
    # This affects all viewsets that inherit from BaseModelViewSet
    # (ProductLineViewSet, ProductViewSet, OfficeViewSet, EmployeeViewSet,
    #  CustomerViewSet, OrderViewSet)
    from api.v1.classicmodels.views import (
        BaseModelViewSet,
        PaymentViewSet,
        OrderdetailViewSet,
    )
    from authentication.views import CustomTokenObtainPairView, CustomTokenRefreshView

    # Also patch the throttle classes themselves to always allow requests
    from config.throttles import (
        ReadThrottle,
        WriteThrottle,
        LoginThrottle,
        RegisterThrottle,
        TokenRefreshThrottle,
        LogoutThrottle,
        CurrentUserThrottle,
    )

    # Store original allow_request methods
    ReadThrottle._original_allow_request = ReadThrottle.allow_request
    WriteThrottle._original_allow_request = WriteThrottle.allow_request
    LoginThrottle._original_allow_request = LoginThrottle.allow_request
    RegisterThrottle._original_allow_request = RegisterThrottle.allow_request
    TokenRefreshThrottle._original_allow_request = TokenRefreshThrottle.allow_request
    LogoutThrottle._original_allow_request = LogoutThrottle.allow_request
    CurrentUserThrottle._original_allow_request = CurrentUserThrottle.allow_request

    # Create a no-op allow_request method
    def allow_request_always_true(self, request, view):
        return True

    # Patch all throttle classes to always allow requests
    ReadThrottle.allow_request = allow_request_always_true
    WriteThrottle.allow_request = allow_request_always_true
    LoginThrottle.allow_request = allow_request_always_true
    RegisterThrottle.allow_request = allow_request_always_true
    TokenRefreshThrottle.allow_request = allow_request_always_true
    LogoutThrottle.allow_request = allow_request_always_true
    CurrentUserThrottle.allow_request = allow_request_always_true

    # Store original throttle classes for restoration if needed
    BaseModelViewSet._original_throttle_classes = BaseModelViewSet.throttle_classes
    PaymentViewSet._original_throttle_classes = PaymentViewSet.throttle_classes
    OrderdetailViewSet._original_throttle_classes = OrderdetailViewSet.throttle_classes
    CustomTokenObtainPairView._original_throttle_classes = (
        CustomTokenObtainPairView.throttle_classes
    )
    CustomTokenRefreshView._original_throttle_classes = getattr(
        CustomTokenRefreshView, "throttle_classes", []
    )

    # Replace with empty list to disable throttling during tests
    # This prevents HTTP 429 errors when running many tests in sequence
    BaseModelViewSet.throttle_classes = []
    PaymentViewSet.throttle_classes = []
    OrderdetailViewSet.throttle_classes = []
    CustomTokenObtainPairView.throttle_classes = []
    CustomTokenRefreshView.throttle_classes = []

    yield

    # Restore original throttle classes and methods (teardown)
    ReadThrottle.allow_request = ReadThrottle._original_allow_request
    WriteThrottle.allow_request = WriteThrottle._original_allow_request
    LoginThrottle.allow_request = LoginThrottle._original_allow_request
    RegisterThrottle.allow_request = RegisterThrottle._original_allow_request
    TokenRefreshThrottle.allow_request = TokenRefreshThrottle._original_allow_request
    LogoutThrottle.allow_request = LogoutThrottle._original_allow_request
    CurrentUserThrottle.allow_request = CurrentUserThrottle._original_allow_request

    BaseModelViewSet.throttle_classes = getattr(
        BaseModelViewSet, "_original_throttle_classes", []
    )
    PaymentViewSet.throttle_classes = getattr(
        PaymentViewSet, "_original_throttle_classes", []
    )
    OrderdetailViewSet.throttle_classes = getattr(
        OrderdetailViewSet, "_original_throttle_classes", []
    )
    CustomTokenObtainPairView.throttle_classes = getattr(
        CustomTokenObtainPairView, "_original_throttle_classes", []
    )
    if hasattr(CustomTokenRefreshView, "_original_throttle_classes"):
        CustomTokenRefreshView.throttle_classes = (
            CustomTokenRefreshView._original_throttle_classes
        )


@pytest.fixture
def api_client():
    """API client for testing endpoints."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def django_client():
    """Django test client for testing views."""
    from django.test import Client

    return Client()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """API client with authentication."""
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def user():
    """Create a test user."""
    from django.contrib.auth.models import User

    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    from django.contrib.auth.models import User

    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def office():
    """Create a test office."""
    from classicmodels.models import Office

    return Office.objects.create(
        officecode="TEST001",
        city="Test City",
        phone="+1-555-0123",
        addressline1="123 Test Street",
        country="USA",
        postalcode="12345",
        territory="NA",
    )


@pytest.fixture
def employee(office):
    """Create a test employee."""
    from classicmodels.models import Employee

    return Employee.objects.create(
        employeenumber=1001,
        lastname="Doe",
        firstname="John",
        extension="1234",
        email="john.doe@example.com",
        officecode=office,
        jobtitle="Sales Rep",
    )


@pytest.fixture
def manager_employee(office):
    """Create a test manager employee."""
    from classicmodels.models import Employee

    return Employee.objects.create(
        employeenumber=1000,
        lastname="Smith",
        firstname="Jane",
        extension="5678",
        email="jane.smith@example.com",
        officecode=office,
        jobtitle="Sales Manager",
    )


@pytest.fixture
def customer(employee):
    """Create a test customer."""
    from classicmodels.models import Customer

    return Customer.objects.create(
        customernumber=1001,
        customername="Test Customer Inc.",
        contactlastname="Johnson",
        contactfirstname="Bob",
        phone="+1-555-0456",
        addressline1="456 Customer Ave",
        city="Customer City",
        country="USA",
        salesrepemployeenumber=employee,
        creditlimit=50000.00,
    )


@pytest.fixture
def product_line():
    """Create a test product line."""
    from classicmodels.models import ProductLine

    return ProductLine.objects.create(
        productline="Test Line",
        textdescription="Test product line description",
        htmldescription="<p>Test HTML description</p>",
    )


@pytest.fixture
def product(product_line):
    """Create a test product."""
    from classicmodels.models import Product

    return Product.objects.create(
        productcode="TEST001",
        productname="Test Product",
        productline=product_line,
        productscale="1:10",
        productvendor="Test Vendor",
        productdescription="A test product for testing purposes",
        quantityinstock=100,
        buyprice=25.50,
        msrp=45.99,
    )


@pytest.fixture
def order(customer):
    """Create a test order."""
    from classicmodels.models import Order

    return Order.objects.create(
        ordernumber=10001,
        orderdate="2024-01-15",
        requireddate="2024-01-20",
        shippeddate="2024-01-18",
        status="Shipped",
        comments="Test order",
        customernumber=customer,
    )


@pytest.fixture
def order_detail(order, product):
    """Create a test order detail."""
    from classicmodels.models import Orderdetail

    return Orderdetail.objects.create(
        ordernumber=order,
        productcode=product,
        quantityordered=5,
        priceeach=45.99,
        orderlinenumber=1,
    )


@pytest.fixture
def payment(customer):
    """Create a test payment."""
    from classicmodels.models import Payment

    return Payment.objects.create(
        customernumber=customer,
        checknumber="TEST001",
        paymentdate="2024-01-20",
        amount=229.95,
    )


@pytest.fixture
def multiple_offices():
    """Create multiple test offices."""
    from classicmodels.models import Office

    offices = []
    for i in range(3):
        office = Office.objects.create(
            officecode=f"OFF{i+1:03d}",
            city=f"City {i+1}",
            phone=f"+1-555-{1000+i:04d}",
            addressline1=f"{100+i} Street",
            country="USA",
            postalcode=f"{10000+i}",
            territory="NA",
        )
        offices.append(office)
    return offices


@pytest.fixture
def multiple_products(product_line):
    """Create multiple test products."""
    from classicmodels.models import Product

    products = []
    for i in range(5):
        product = Product.objects.create(
            productcode=f"PROD{i+1:03d}",
            productname=f"Product {i+1}",
            productline=product_line,
            productscale="1:10",
            productvendor=f"Vendor {i+1}",
            productdescription=f"Description for product {i+1}",
            quantityinstock=50 + i * 10,
            buyprice=20.00 + i * 5.00,
            msrp=35.00 + i * 8.00,
        )
        products.append(product)
    return products


@pytest.fixture
def sample_data(
    office, employee, customer, product_line, product, order, order_detail, payment
):
    """Create a complete set of sample data for testing."""
    return {
        "office": office,
        "employee": employee,
        "customer": customer,
        "product_line": product_line,
        "product": product,
        "order": order,
        "order_detail": order_detail,
        "payment": payment,
    }
