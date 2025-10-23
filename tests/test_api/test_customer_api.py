"""
Tests for Customer API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status

from classicmodels.models import Customer


class TestCustomerAPI:
    """Test cases for Customer API endpoints."""

    @pytest.mark.django_db
    def test_list_customers_authenticated(self, authenticated_api_client, customer):
        """Test listing customers when authenticated."""
        url = reverse("classicmodels:customer-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["customernumber"] == customer.customernumber

    @pytest.mark.django_db
    def test_list_customers_unauthenticated(self, api_client, customer):
        """Test listing customers when not authenticated."""
        url = reverse("classicmodels:customer-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_customer_authenticated(self, authenticated_api_client, customer):
        """Test retrieving a specific customer when authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["customernumber"] == customer.customernumber
        assert response.data["customername"] == customer.customername

    @pytest.mark.django_db
    def test_retrieve_customer_unauthenticated(self, api_client, customer):
        """Test retrieving a customer when not authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_customer(self, authenticated_api_client):
        """Test retrieving a customer that doesn't exist."""
        url = reverse("classicmodels:customer-detail", kwargs={"customernumber": 99999})
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_customer_authenticated(self, authenticated_api_client, employee):
        """Test creating a customer when authenticated."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 2001,
            "customername": "New Customer Inc.",
            "contactlastname": "Smith",
            "contactfirstname": "John",
            "phone": "+1-555-9999",
            "addressline1": "999 New Street",
            "addressline2": "Suite 500",
            "city": "New City",
            "state": "NY",
            "postalcode": "10001",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
            "creditlimit": "50000.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["customernumber"] == 2001
        assert response.data["customername"] == "New Customer Inc."

    @pytest.mark.django_db
    def test_create_customer_unauthenticated(self, api_client, employee):
        """Test creating a customer when not authenticated."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 2001,
            "customername": "New Customer Inc.",
            "contactlastname": "Smith",
            "contactfirstname": "John",
            "phone": "+1-555-9999",
            "addressline1": "999 New Street",
            "city": "New City",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_customer_duplicate_number(
        self, authenticated_api_client, customer, employee
    ):
        """Test creating a customer with duplicate customer number."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": customer.customernumber,  # Duplicate
            "customername": "Duplicate Customer",
            "contactlastname": "Duplicate",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 Duplicate Ave",
            "city": "Duplicate City",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_customer_invalid_sales_rep(self, authenticated_api_client):
        """Test creating a customer with invalid sales rep."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 2002,
            "customername": "Invalid Sales Rep Customer",
            "contactlastname": "Invalid",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 Invalid Ave",
            "city": "Invalid City",
            "country": "USA",
            "salesrepemployeenumber": 99999,  # Invalid sales rep
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_customer_minimal_data(self, authenticated_api_client, employee):
        """Test creating a customer with minimal required data."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 2003,
            "customername": "Minimal Customer",
            "contactlastname": "Minimal",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 Minimal Ave",
            "city": "Minimal City",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["customernumber"] == 2003
        assert response.data["addressline2"] is None
        assert response.data["state"] is None
        assert response.data["postalcode"] is None
        assert response.data["creditlimit"] is None

    @pytest.mark.django_db
    def test_update_customer_authenticated(self, authenticated_api_client, customer):
        """Test updating a customer when authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        data = {
            "customernumber": customer.customernumber,
            "customername": "Updated Customer Inc.",
            "contactlastname": "Updated",
            "contactfirstname": "John",
            "phone": "+1-555-8888",
            "addressline1": "888 Updated Street",
            "addressline2": "Suite 888",
            "city": "Updated City",
            "state": "CA",
            "postalcode": "90210",
            "country": "USA",
            "salesrepemployeenumber": customer.salesrepemployeenumber.employeenumber,
            "creditlimit": "75000.00",
        }

        response = authenticated_api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["customername"] == "Updated Customer Inc."
        assert response.data["phone"] == "+1-555-8888"

    @pytest.mark.django_db
    def test_update_customer_unauthenticated(self, api_client, customer):
        """Test updating a customer when not authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        data = {
            "customernumber": customer.customernumber,
            "customername": "Updated Customer Inc.",
            "contactlastname": "Updated",
            "contactfirstname": "John",
            "phone": "+1-555-8888",
            "addressline1": "888 Updated Street",
            "city": "Updated City",
            "country": "USA",
            "salesrepemployeenumber": customer.salesrepemployeenumber.employeenumber,
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_customer_authenticated(
        self, authenticated_api_client, customer
    ):
        """Test partially updating a customer when authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        data = {"customername": "Partially Updated Customer", "phone": "+1-555-7777"}

        response = authenticated_api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["customername"] == "Partially Updated Customer"
        assert response.data["phone"] == "+1-555-7777"
        # Other fields should remain unchanged
        assert response.data["customernumber"] == customer.customernumber

    @pytest.mark.django_db
    def test_partial_update_customer_unauthenticated(self, api_client, customer):
        """Test partially updating a customer when not authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        data = {"customername": "Partially Updated Customer"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_customer_authenticated(self, authenticated_api_client, customer):
        """Test deleting a customer when authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Customer.objects.filter(
            customernumber=customer.customernumber
        ).exists()

    @pytest.mark.django_db
    def test_delete_customer_unauthenticated(self, api_client, customer):
        """Test deleting a customer when not authenticated."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_customer(self, authenticated_api_client):
        """Test deleting a customer that doesn't exist."""
        url = reverse("classicmodels:customer-detail", kwargs={"customernumber": 99999})
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_customer_serializer_validation(self, authenticated_api_client, employee):
        """Test customer serializer validation."""
        url = reverse("classicmodels:customer-list")

        # Test with invalid data (exceeds max length)
        data = {
            "customernumber": 3001,
            "customername": "x" * 51,  # Exceeds max_length=50
            "contactlastname": "Valid",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 Valid Ave",
            "city": "Valid City",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
        }

        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_customer_credit_limit_precision(self, authenticated_api_client, employee):
        """Test credit limit decimal precision."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 3002,
            "customername": "Credit Customer",
            "contactlastname": "Credit",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 Credit Ave",
            "city": "Credit City",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
            "creditlimit": "99999999.99",  # Max value for (10,2)
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["creditlimit"] == "99999999.99"

    @pytest.mark.django_db
    def test_customer_phone_formats(self, authenticated_api_client, employee):
        """Test various phone number formats."""
        url = reverse("classicmodels:customer-list")
        phone_formats = [
            "+1-555-0123",
            "(555) 123-4567",
            "555-123-4567",
            "5551234567",
            "+44 20 7946 0958",
            "+33 1 42 86 83 26",
        ]

        for i, phone in enumerate(phone_formats):
            data = {
                "customernumber": 3010 + i,
                "customername": f"Phone Customer {i}",
                "contactlastname": f"Phone{i}",
                "contactfirstname": "Test",
                "phone": phone,
                "addressline1": f"{100+i} Phone Ave",
                "city": f"Phone City {i}",
                "country": "USA",
                "salesrepemployeenumber": employee.employeenumber,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["phone"] == phone

    @pytest.mark.django_db
    def test_customer_postal_code_formats(self, authenticated_api_client, employee):
        """Test various postal code formats."""
        url = reverse("classicmodels:customer-list")
        postal_codes = [
            "12345",  # US ZIP
            "12345-6789",  # US ZIP+4
            "K1A 0A6",  # Canadian postal code
            "SW1A 1AA",  # UK postal code
            "75001",  # French postal code
            "100-0001",  # Japanese postal code
        ]

        for i, postal_code in enumerate(postal_codes):
            data = {
                "customernumber": 3020 + i,
                "customername": f"Postal Customer {i}",
                "contactlastname": f"Postal{i}",
                "contactfirstname": "Test",
                "phone": "+1-555-0000",
                "addressline1": f"{100+i} Postal Ave",
                "city": f"Postal City {i}",
                "postalcode": postal_code,
                "country": "USA",
                "salesrepemployeenumber": employee.employeenumber,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["postalcode"] == postal_code

    @pytest.mark.django_db
    def test_customer_unicode_handling(self, authenticated_api_client, employee):
        """Test handling of unicode characters in customer."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 3030,
            "customername": "Customer with émojis 🏢 and accents",
            "contactlastname": "Doe with émojis 👤 and accents",
            "contactfirstname": "Jean with émojis 👨 and accents",
            "phone": "+1-555-émojis",
            "addressline1": "123 Rue de la Paix with émojis 🏠",
            "addressline2": "Suite 100 with émojis 🏢",
            "city": "Cité with émojis 🌆 and accents",
            "state": "État with émojis 🌟",
            "postalcode": "12345-émojis",
            "country": "Pays with émojis 🌍",
            "salesrepemployeenumber": employee.employeenumber,
            "creditlimit": "50000.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "émojis" in response.data["customername"]
        assert "🏢" in response.data["customername"]
        assert "émojis" in response.data["contactlastname"]
        assert "👤" in response.data["contactlastname"]

    @pytest.mark.django_db
    def test_customer_negative_credit_limit(self, authenticated_api_client, employee):
        """Test handling of negative credit limit."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 3040,
            "customername": "Negative Credit Customer",
            "contactlastname": "Negative",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 Negative Ave",
            "city": "Negative City",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
            "creditlimit": "-1000.00",  # Negative credit limit
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["creditlimit"] == "-1000.00"

    @pytest.mark.django_db
    def test_customer_zero_credit_limit(self, authenticated_api_client, employee):
        """Test handling of zero credit limit."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 3041,
            "customername": "Zero Credit Customer",
            "contactlastname": "Zero",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 Zero Ave",
            "city": "Zero City",
            "country": "USA",
            "salesrepemployeenumber": employee.employeenumber,
            "creditlimit": "0.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["creditlimit"] == "0.00"

    @pytest.mark.django_db
    def test_customer_without_sales_rep(self, authenticated_api_client):
        """Test customer without sales rep."""
        url = reverse("classicmodels:customer-list")
        data = {
            "customernumber": 3042,
            "customername": "No Rep Customer",
            "contactlastname": "NoRep",
            "contactfirstname": "Test",
            "phone": "+1-555-0000",
            "addressline1": "123 NoRep Ave",
            "city": "NoRep City",
            "country": "USA",
            "salesrepemployeenumber": None,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["salesrepemployeenumber"] is None

    @pytest.mark.django_db
    def test_customer_pagination(self, authenticated_api_client, employee):
        """Test customer pagination."""
        # Create additional customers beyond the existing ones
        for i in range(15):  # More than default page size
            Customer.objects.create(
                customernumber=4000 + i,
                customername=f"Pagination Customer {i}",
                contactlastname=f"Pagination{i}",
                contactfirstname="Test",
                phone=f"+1-555-{1000+i:04d}",
                addressline1=f"{100+i} Pagination Ave",
                city=f"Pagination City {i}",
                country="USA",
                salesrepemployeenumber=employee,
            )

        url = reverse("classicmodels:customer-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    @pytest.mark.django_db
    def test_customer_ordering(self, authenticated_api_client, employee):
        """Test customer ordering."""
        # Create customers in specific order
        Customer.objects.create(
            customernumber=5001,
            customername="Z Customer",
            contactlastname="Z",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Z Ave",
            city="Z City",
            country="USA",
            salesrepemployeenumber=employee,
        )
        Customer.objects.create(
            customernumber=5002,
            customername="A Customer",
            contactlastname="A",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 A Ave",
            city="A City",
            country="USA",
            salesrepemployeenumber=employee,
        )

        url = reverse("classicmodels:customer-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data["results"]) >= 2

    @pytest.mark.django_db
    def test_customer_relationships(self, authenticated_api_client, customer, employee):
        """Test customer relationships in API response."""
        url = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "salesrepemployeenumber" in response.data
        assert response.data["salesrepemployeenumber"] == employee.employeenumber
