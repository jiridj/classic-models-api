"""
Tests for Payment API endpoints.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from classicmodels.models import Customer, Payment


class TestPaymentAPI:
    """Test cases for Payment API endpoints."""

    @pytest.mark.django_db
    def test_list_payments_authenticated(self, authenticated_api_client, payment):
        """Test listing payments when authenticated."""
        url = reverse("classicmodels:payment-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        # Verify id field is present in response
        assert "id" in response.data["results"][0]
        assert response.data["results"][0]["id"] == payment.id
        assert (
            response.data["results"][0]["customernumber"]
            == payment.customernumber.customernumber
        )
        assert response.data["results"][0]["checknumber"] == payment.checknumber

    @pytest.mark.django_db
    def test_list_payments_unauthenticated(self, api_client, payment):
        """Test listing payments when not authenticated."""
        url = reverse("classicmodels:payment-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_payment_authenticated(self, authenticated_api_client, payment):
        """Test retrieving a specific payment when authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Verify id field is present in response
        assert "id" in response.data
        assert response.data["id"] == payment.id
        assert response.data["customernumber"] == payment.customernumber.customernumber
        assert response.data["checknumber"] == payment.checknumber

    @pytest.mark.django_db
    def test_retrieve_payment_unauthenticated(self, api_client, payment):
        """Test retrieving a payment when not authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_payment(self, authenticated_api_client, customer):
        """Test retrieving a payment that doesn't exist."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": customer.customernumber,
                "checkNumber": "NONEXISTENT",
            },
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_payment_authenticated(self, authenticated_api_client, customer):
        """Test creating a payment when authenticated."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": customer.customernumber,
            "checknumber": "NEW001",
            "paymentdate": "2024-02-20",
            "amount": "150.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # Verify id field is present and auto-generated in response
        assert "id" in response.data
        assert isinstance(response.data["id"], int)
        assert response.data["customernumber"] == customer.customernumber
        assert response.data["checknumber"] == "NEW001"

    @pytest.mark.django_db
    def test_create_payment_unauthenticated(self, api_client, customer):
        """Test creating a payment when not authenticated."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": customer.customernumber,
            "checknumber": "NEW001",
            "paymentdate": "2024-02-20",
            "amount": "150.00",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_payment_duplicate(self, authenticated_api_client, payment):
        """Test creating a payment with duplicate customer and check number."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": payment.customernumber.customernumber,
            "checknumber": payment.checknumber,  # Duplicate
            "paymentdate": "2024-02-21",
            "amount": "200.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_payment_invalid_customer(self, authenticated_api_client):
        """Test creating a payment with invalid customer."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": 99999,  # Invalid customer
            "checknumber": "INVALID001",
            "paymentdate": "2024-02-20",
            "amount": "100.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_payment_same_check_different_customers(
        self, authenticated_api_client, customer, employee
    ):
        """Test creating payments with same check number for different customers."""
        # Create another customer
        customer2 = Customer.objects.create(
            customernumber=2001,
            customername="Second Customer",
            contactlastname="Second",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Second Ave",
            city="Second City",
            country="USA",
            salesrepemployeenumber=employee,
        )

        url = reverse("classicmodels:payment-list")

        # First payment
        data1 = {
            "customernumber": customer.customernumber,
            "checknumber": "SAME001",
            "paymentdate": "2024-02-20",
            "amount": "100.00",
        }

        response1 = authenticated_api_client.post(url, data1, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Second payment with same check number, different customer
        data2 = {
            "customernumber": customer2.customernumber,
            "checknumber": "SAME001",  # Same check number
            "paymentdate": "2024-02-21",
            "amount": "200.00",
        }

        response2 = authenticated_api_client.post(url, data2, format="json")
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.data["customernumber"] == customer2.customernumber
        assert response2.data["checknumber"] == "SAME001"

    @pytest.mark.django_db
    def test_update_payment_authenticated(self, authenticated_api_client, payment):
        """Test updating a payment when authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        data = {
            "customernumber": payment.customernumber.customernumber,
            "checknumber": payment.checknumber,
            "paymentdate": "2024-02-21",
            "amount": "300.00",
        }

        response = authenticated_api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == "300.00"
        assert response.data["paymentdate"] == "2024-02-21"

    @pytest.mark.django_db
    def test_update_payment_unauthenticated(self, api_client, payment):
        """Test updating a payment when not authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        data = {
            "customernumber": payment.customernumber.customernumber,
            "checknumber": payment.checknumber,
            "paymentdate": "2024-02-21",
            "amount": "300.00",
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_payment_authenticated(
        self, authenticated_api_client, payment
    ):
        """Test partially updating a payment when authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        data = {"amount": "250.00"}

        response = authenticated_api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == "250.00"
        # Other fields should remain unchanged
        assert response.data["customernumber"] == payment.customernumber.customernumber
        assert response.data["checknumber"] == payment.checknumber

    @pytest.mark.django_db
    def test_partial_update_payment_unauthenticated(self, api_client, payment):
        """Test partially updating a payment when not authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        data = {"amount": "250.00"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_payment_authenticated(self, authenticated_api_client, payment):
        """Test deleting a payment when authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Payment.objects.filter(
            customernumber=payment.customernumber, checknumber=payment.checknumber
        ).exists()

    @pytest.mark.django_db
    def test_delete_payment_unauthenticated(self, api_client, payment):
        """Test deleting a payment when not authenticated."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_payment(self, authenticated_api_client, customer):
        """Test deleting a payment that doesn't exist."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": customer.customernumber,
                "checkNumber": "NONEXISTENT",
            },
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_payment_serializer_validation(self, authenticated_api_client, customer):
        """Test payment serializer validation."""
        url = reverse("classicmodels:payment-list")

        # Test with invalid data (exceeds max length)
        data = {
            "customernumber": customer.customernumber,
            "checknumber": "x" * 51,  # Exceeds max_length=50
            "paymentdate": "2024-02-20",
            "amount": "100.00",
        }

        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_payment_decimal_precision(self, authenticated_api_client, customer):
        """Test decimal field precision and rounding."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": customer.customernumber,
            "checknumber": "PREC001",
            "paymentdate": "2024-02-20",
            "amount": "12.35",  # Valid 2 decimal places
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == "12.35"

    @pytest.mark.django_db
    def test_payment_negative_amount(self, authenticated_api_client, customer):
        """Test handling of negative amounts."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": customer.customernumber,
            "checknumber": "NEG001",
            "paymentdate": "2024-02-20",
            "amount": "-100.00",  # Negative amount (refund)
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == "-100.00"

    @pytest.mark.django_db
    def test_payment_zero_amount(self, authenticated_api_client, customer):
        """Test handling of zero amounts."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": customer.customernumber,
            "checknumber": "ZERO001",
            "paymentdate": "2024-02-20",
            "amount": "0.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == "0.00"

    @pytest.mark.django_db
    def test_payment_check_number_formats(self, authenticated_api_client, customer):
        """Test various check number formats."""
        url = reverse("classicmodels:payment-list")
        check_numbers = [
            "CHK001",
            "123456",
            "CHK-001",
            "123-456-789",
            "CHK001A",
            "001234567890",
            "CHK-001-2024",
        ]

        for i, check_number in enumerate(check_numbers):
            data = {
                "customernumber": customer.customernumber,
                "checknumber": check_number,
                "paymentdate": "2024-02-20",
                "amount": "100.00",
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["checknumber"] == check_number

    @pytest.mark.django_db
    def test_payment_date_variations(self, authenticated_api_client, customer):
        """Test various payment dates."""
        url = reverse("classicmodels:payment-list")
        dates = [
            "2024-01-01",  # New Year
            "2024-02-29",  # Leap year
            "2024-06-15",  # Mid year
            "2024-12-31",  # End of year
            "2020-01-01",  # Past date
            "2030-01-01",  # Future date
        ]

        for i, payment_date in enumerate(dates):
            data = {
                "customernumber": customer.customernumber,
                "checknumber": f"DATE{i:03d}",
                "paymentdate": payment_date,
                "amount": "100.00",
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["paymentdate"] == payment_date

    @pytest.mark.django_db
    def test_payment_unicode_handling(self, authenticated_api_client, customer):
        """Test handling of unicode characters in check number."""
        url = reverse("classicmodels:payment-list")
        data = {
            "customernumber": customer.customernumber,
            "checknumber": "CHK with émojis 💰 and accents",
            "paymentdate": "2024-02-20",
            "amount": "100.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "émojis" in response.data["checknumber"]
        assert "💰" in response.data["checknumber"]
        assert "accents" in response.data["checknumber"]

    @pytest.mark.django_db
    def test_payment_large_check_number(self, authenticated_api_client, customer):
        """Test handling of large check numbers."""
        url = reverse("classicmodels:payment-list")
        large_check_number = "x" * 50  # Max length

        data = {
            "customernumber": customer.customernumber,
            "checknumber": large_check_number,
            "paymentdate": "2024-02-20",
            "amount": "100.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["checknumber"] == large_check_number
        assert len(response.data["checknumber"]) == 50

    @pytest.mark.django_db
    def test_payment_multiple_payments_same_customer(
        self, authenticated_api_client, customer
    ):
        """Test multiple payments for the same customer."""
        url = reverse("classicmodels:payment-list")

        for i in range(5):
            data = {
                "customernumber": customer.customernumber,
                "checknumber": f"MULT{i:03d}",
                "paymentdate": f"2024-02-{20+i:02d}",
                "amount": f"{100.00 + i * 10.00}",
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["customernumber"] == customer.customernumber

    @pytest.mark.django_db
    def test_payment_amount_precision_rounding(
        self, authenticated_api_client, customer
    ):
        """Test amount field precision and rounding."""
        url = reverse("classicmodels:payment-list")
        test_amounts = [
            ("12.35", "12.35"),  # Valid 2 decimal places
            ("12.34", "12.34"),  # Valid 2 decimal places
            ("12.36", "12.36"),  # Valid 2 decimal places
            ("12.34", "12.34"),  # Valid 2 decimal places
        ]

        for i, (input_amount, expected_amount) in enumerate(test_amounts):
            data = {
                "customernumber": customer.customernumber,
                "checknumber": f"ROUND{i:03d}",
                "paymentdate": "2024-02-20",
                "amount": input_amount,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["amount"] == expected_amount

    @pytest.mark.django_db
    def test_payment_very_small_amounts(self, authenticated_api_client, customer):
        """Test handling of very small amounts."""
        url = reverse("classicmodels:payment-list")
        small_amounts = ["0.01", "0.10", "0.99"]  # 1 cent, 10 cents, 99 cents

        for i, amount in enumerate(small_amounts):
            data = {
                "customernumber": customer.customernumber,
                "checknumber": f"SMALL{i:03d}",
                "paymentdate": "2024-02-20",
                "amount": amount,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["amount"] == amount

    @pytest.mark.django_db
    def test_payment_very_large_amounts(self, authenticated_api_client, customer):
        """Test handling of very large amounts."""
        url = reverse("classicmodels:payment-list")
        large_amounts = [
            "99999999.99",
            "1000000.00",
            "5000000.50",
        ]  # Max value, 1 million, 5 million

        for i, amount in enumerate(large_amounts):
            data = {
                "customernumber": customer.customernumber,
                "checknumber": f"LARGE{i:03d}",
                "paymentdate": "2024-02-20",
                "amount": amount,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["amount"] == amount

    @pytest.mark.django_db
    def test_payment_pagination(self, authenticated_api_client, customer):
        """Test payment pagination."""
        # Create additional payments beyond the existing ones
        for i in range(15):  # More than default page size
            Payment.objects.create(
                customernumber=customer,
                checknumber=f"PAGE{i:03d}",
                paymentdate="2024-02-20",
                amount=Decimal("100.00"),
            )

        url = reverse("classicmodels:payment-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    @pytest.mark.django_db
    def test_payment_ordering(self, authenticated_api_client, customer):
        """Test payment ordering."""
        # Create payments in specific order
        Payment.objects.create(
            customernumber=customer,
            checknumber="ZPAY001",
            paymentdate="2024-02-20",
            amount=Decimal("100.00"),
        )
        Payment.objects.create(
            customernumber=customer,
            checknumber="APAY001",
            paymentdate="2024-02-21",
            amount=Decimal("200.00"),
        )

        url = reverse("classicmodels:payment-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data["results"]) >= 2

    @pytest.mark.django_db
    def test_payment_relationships(self, authenticated_api_client, payment, customer):
        """Test payment relationships in API response."""
        url = reverse(
            "classicmodels:payment-detail",
            kwargs={
                "customerNumber": payment.customernumber.customernumber,
                "checkNumber": payment.checknumber,
            },
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "customernumber" in response.data
        assert response.data["customernumber"] == customer.customernumber
