"""
Test utilities and helper functions for the Classic Models API tests.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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


class TestDataFactory:
    """Factory class for creating test data."""

    @staticmethod
    def create_user(
        username="testuser", email="test@example.com", password="testpass123", **kwargs
    ):
        """Create a test user."""
        return User.objects.create_user(
            username=username, email=email, password=password, **kwargs
        )

    @staticmethod
    def create_office(officecode="TEST001", **kwargs):
        """Create a test office."""
        defaults = {
            "city": "Test City",
            "phone": "+1-555-0123",
            "addressline1": "123 Test Street",
            "country": "USA",
            "postalcode": "12345",
            "territory": "NA",
        }
        defaults.update(kwargs)
        return Office.objects.create(officecode=officecode, **defaults)

    @staticmethod
    def create_employee(employeenumber=1001, office=None, **kwargs):
        """Create a test employee."""
        if office is None:
            office = TestDataFactory.create_office()

        defaults = {
            "lastname": "Doe",
            "firstname": "John",
            "extension": "1234",
            "email": "john.doe@example.com",
            "officecode": office,
            "jobtitle": "Sales Rep",
        }
        defaults.update(kwargs)
        return Employee.objects.create(employeenumber=employeenumber, **defaults)

    @staticmethod
    def create_customer(customernumber=1001, employee=None, **kwargs):
        """Create a test customer."""
        if employee is None:
            office = TestDataFactory.create_office()
            employee = TestDataFactory.create_employee(office=office)

        defaults = {
            "customername": "Test Customer Inc.",
            "contactlastname": "Johnson",
            "contactfirstname": "Bob",
            "phone": "+1-555-0456",
            "addressline1": "456 Customer Ave",
            "city": "Customer City",
            "country": "USA",
            "salesrepemployeenumber": employee,
            "creditlimit": Decimal("50000.00"),
        }
        defaults.update(kwargs)
        return Customer.objects.create(customernumber=customernumber, **defaults)

    @staticmethod
    def create_product_line(productline="Test Line", **kwargs):
        """Create a test product line."""
        defaults = {
            "textdescription": "Test product line description",
            "htmldescription": "<p>Test HTML description</p>",
        }
        defaults.update(kwargs)
        return ProductLine.objects.create(productline=productline, **defaults)

    @staticmethod
    def create_product(productcode="TEST001", product_line=None, **kwargs):
        """Create a test product."""
        if product_line is None:
            product_line = TestDataFactory.create_product_line()

        defaults = {
            "productname": "Test Product",
            "productline": product_line,
            "productscale": "1:10",
            "productvendor": "Test Vendor",
            "productdescription": "A test product for testing purposes",
            "quantityinstock": 100,
            "buyprice": Decimal("25.50"),
            "msrp": Decimal("45.99"),
        }
        defaults.update(kwargs)
        return Product.objects.create(productcode=productcode, **defaults)

    @staticmethod
    def create_order(ordernumber=10001, customer=None, **kwargs):
        """Create a test order."""
        if customer is None:
            customer = TestDataFactory.create_customer()

        defaults = {
            "orderdate": date(2024, 1, 15),
            "requireddate": date(2024, 1, 20),
            "shippeddate": date(2024, 1, 18),
            "status": "Shipped",
            "comments": "Test order",
            "customernumber": customer,
        }
        defaults.update(kwargs)
        return Order.objects.create(ordernumber=ordernumber, **defaults)

    @staticmethod
    def create_order_detail(order=None, product=None, **kwargs):
        """Create a test order detail."""
        if order is None:
            order = TestDataFactory.create_order()
        if product is None:
            product = TestDataFactory.create_product()

        defaults = {
            "ordernumber": order,
            "productcode": product,
            "quantityordered": 5,
            "priceeach": Decimal("45.99"),
            "orderlinenumber": 1,
        }
        defaults.update(kwargs)
        return Orderdetail.objects.create(**defaults)

    @staticmethod
    def create_payment(customer=None, checknumber="TEST001", **kwargs):
        """Create a test payment."""
        if customer is None:
            customer = TestDataFactory.create_customer()

        defaults = {
            "customernumber": customer,
            "checknumber": checknumber,
            "paymentdate": date(2024, 1, 20),
            "amount": Decimal("229.95"),
        }
        defaults.update(kwargs)
        return Payment.objects.create(**defaults)


class APITestCase(TestCase):
    """Base test case for API tests with common setup."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = TestDataFactory.create_user()
        self.office = TestDataFactory.create_office()
        self.employee = TestDataFactory.create_employee(office=self.office)
        self.customer = TestDataFactory.create_customer(employee=self.employee)
        self.product_line = TestDataFactory.create_product_line()
        self.product = TestDataFactory.create_product(product_line=self.product_line)
        self.order = TestDataFactory.create_order(customer=self.customer)
        self.order_detail = TestDataFactory.create_order_detail(
            order=self.order, product=self.product
        )
        self.payment = TestDataFactory.create_payment(customer=self.customer)

    def authenticate_user(self, user=None):
        """Authenticate a user for API requests."""
        if user is None:
            user = self.user

        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return user

    def create_authenticated_client(self, user=None):
        """Create an authenticated API client."""
        if user is None:
            user = self.user

        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        return client


class ModelTestMixin:
    """Mixin with common model test utilities."""

    def assert_model_field_attributes(
        self, model_class, field_name, **expected_attributes
    ):
        """Assert that a model field has the expected attributes."""
        field = model_class._meta.get_field(field_name)
        for attr_name, expected_value in expected_attributes.items():
            actual_value = getattr(field, attr_name)
            assert (
                actual_value == expected_value
            ), f"Field {field_name}.{attr_name} expected {expected_value}, got {actual_value}"

    def assert_model_meta_options(self, model_class, **expected_options):
        """Assert that a model has the expected meta options."""
        for option_name, expected_value in expected_options.items():
            actual_value = getattr(model_class._meta, option_name)
            assert (
                actual_value == expected_value
            ), f"Model {model_class.__name__}.{option_name} expected {expected_value}, got {actual_value}"

    def assert_unique_constraint(self, model_class, field_values, should_raise=True):
        """Assert that a unique constraint is enforced."""
        if should_raise:
            with pytest.raises(Exception):  # Could be IntegrityError or ValidationError
                model_class.objects.create(**field_values)
        else:
            # Should not raise an exception
            instance = model_class.objects.create(**field_values)
            assert instance is not None


class APITestMixin:
    """Mixin with common API test utilities."""

    def assert_api_response_status(self, response, expected_status):
        """Assert that an API response has the expected status code."""
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response data: {response.data}"
        )

    def assert_api_response_contains(self, response, expected_keys):
        """Assert that an API response contains the expected keys."""
        if isinstance(expected_keys, str):
            expected_keys = [expected_keys]

        for key in expected_keys:
            assert (
                key in response.data
            ), f"Response missing key: {key}. Response data: {response.data}"

    def assert_api_response_data(self, response, expected_data):
        """Assert that an API response data matches expected data."""
        for key, expected_value in expected_data.items():
            actual_value = response.data.get(key)
            assert (
                actual_value == expected_value
            ), f"Response data mismatch for key '{key}': expected {expected_value}, got {actual_value}"

    def assert_api_pagination(self, response):
        """Assert that an API response has pagination structure."""
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data
        assert isinstance(response.data["results"], list)

    def assert_api_error_response(self, response, expected_status=400):
        """Assert that an API response is an error response."""
        self.assert_api_response_status(response, expected_status)
        assert (
            "errors" in response.data
            or "error" in response.data
            or "detail" in response.data
        )


class DataValidationMixin:
    """Mixin with data validation utilities."""

    def assert_decimal_precision(self, value, expected_digits, expected_places):
        """Assert that a decimal value has the correct precision."""
        if isinstance(value, str):
            value = Decimal(value)

        # Check that the value can be represented with the given precision
        max_value = Decimal("9" * (expected_digits - expected_places)) + Decimal(
            "0." + "9" * expected_places
        )
        assert (
            value <= max_value
        ), f"Value {value} exceeds precision {expected_digits},{expected_places}"

    def assert_max_length_constraint(self, field_value, max_length):
        """Assert that a field value respects max length constraint."""
        if field_value is not None:
            assert (
                len(str(field_value)) <= max_length
            ), f"Field value '{field_value}' exceeds max length {max_length}"

    def assert_required_field(self, model_class, field_name, test_data):
        """Assert that a field is required by testing without it."""
        # Remove the field from test data
        test_data_without_field = test_data.copy()
        test_data_without_field.pop(field_name, None)

        with pytest.raises(Exception):  # Could be IntegrityError or ValidationError
            model_class.objects.create(**test_data_without_field)


class DataBuilder:
    """Builder pattern for creating complex test data."""

    def __init__(self):
        self.data = {}

    def with_user(self, **user_data):
        """Add user data to the builder."""
        self.data["user"] = TestDataFactory.create_user(**user_data)
        return self

    def with_office(self, **office_data):
        """Add office data to the builder."""
        self.data["office"] = TestDataFactory.create_office(**office_data)
        return self

    def with_employee(self, **employee_data):
        """Add employee data to the builder."""
        if "office" not in self.data:
            self.with_office()
        self.data["employee"] = TestDataFactory.create_employee(
            office=self.data["office"], **employee_data
        )
        return self

    def with_customer(self, **customer_data):
        """Add customer data to the builder."""
        if "employee" not in self.data:
            self.with_employee()
        self.data["customer"] = TestDataFactory.create_customer(
            employee=self.data["employee"], **customer_data
        )
        return self

    def with_product_line(self, **product_line_data):
        """Add product line data to the builder."""
        self.data["product_line"] = TestDataFactory.create_product_line(
            **product_line_data
        )
        return self

    def with_product(self, **product_data):
        """Add product data to the builder."""
        if "product_line" not in self.data:
            self.with_product_line()
        self.data["product"] = TestDataFactory.create_product(
            product_line=self.data["product_line"], **product_data
        )
        return self

    def with_order(self, **order_data):
        """Add order data to the builder."""
        if "customer" not in self.data:
            self.with_customer()
        self.data["order"] = TestDataFactory.create_order(
            customer=self.data["customer"], **order_data
        )
        return self

    def with_order_detail(self, **order_detail_data):
        """Add order detail data to the builder."""
        if "order" not in self.data:
            self.with_order()
        if "product" not in self.data:
            self.with_product()
        self.data["order_detail"] = TestDataFactory.create_order_detail(
            order=self.data["order"], product=self.data["product"], **order_detail_data
        )
        return self

    def with_payment(self, **payment_data):
        """Add payment data to the builder."""
        if "customer" not in self.data:
            self.with_customer()
        self.data["payment"] = TestDataFactory.create_payment(
            customer=self.data["customer"], **payment_data
        )
        return self

    def build(self):
        """Build and return the test data."""
        return self.data


# Utility functions for common test operations
def create_test_hierarchy():
    """Create a complete test hierarchy with all related objects."""
    builder = DataBuilder()
    return (
        builder.with_user()
        .with_office()
        .with_employee()
        .with_customer()
        .with_product_line()
        .with_product()
        .with_order()
        .with_order_detail()
        .with_payment()
        .build()
    )


def create_multiple_objects(model_class, count, **defaults):
    """Create multiple objects of the same type."""
    objects = []
    for i in range(count):
        obj_data = defaults.copy()
        # Add unique identifiers if they exist
        if hasattr(model_class, "officecode"):
            obj_data["officecode"] = f"OFF{i:03d}"
        elif hasattr(model_class, "productcode"):
            obj_data["productcode"] = f"PROD{i:03d}"
        elif hasattr(model_class, "customernumber"):
            obj_data["customernumber"] = 1000 + i
        elif hasattr(model_class, "employeenumber"):
            obj_data["employeenumber"] = 1000 + i
        elif hasattr(model_class, "ordernumber"):
            obj_data["ordernumber"] = 10000 + i

        obj = model_class.objects.create(**obj_data)
        objects.append(obj)

    return objects


def assert_model_relationships(instance, expected_relationships):
    """Assert that model relationships are correctly set."""
    for relationship_name, expected_value in expected_relationships.items():
        actual_value = getattr(instance, relationship_name)
        assert (
            actual_value == expected_value
        ), f"Relationship {relationship_name} expected {expected_value}, got {actual_value}"


def assert_api_endpoint_permissions(
    client, url, method="GET", data=None, expected_status=200
):
    """Assert that an API endpoint has the correct permissions."""
    # Test unauthenticated request
    if method.upper() == "GET":
        response = client.get(url)
    elif method.upper() == "POST":
        response = client.post(url, data, format="json")
    elif method.upper() == "PUT":
        response = client.put(url, data, format="json")
    elif method.upper() == "PATCH":
        response = client.patch(url, data, format="json")
    elif method.upper() == "DELETE":
        response = client.delete(url)

    # Should return 401 for protected endpoints
    assert (
        response.status_code == 401
    ), f"Expected 401 for unauthenticated request, got {response.status_code}"
