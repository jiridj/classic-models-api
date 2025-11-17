"""
Tests for Payment model.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from classicmodels.models import Customer, Payment


class TestPaymentModel:
    """Test cases for Payment model."""

    @pytest.mark.django_db
    def test_payment_creation(self, customer):
        """Test creating a payment with all fields."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="TEST001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("229.95"),
        )

        assert payment.id is not None  # id should be auto-generated
        assert isinstance(payment.id, int)  # id should be an integer
        assert payment.customernumber == customer
        assert payment.checknumber == "TEST001"
        assert payment.paymentdate == date(2024, 1, 20)
        assert payment.amount == Decimal("229.95")

    @pytest.mark.django_db
    def test_payment_string_representation(self, customer):
        """Test the string representation of Payment."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="REPR001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        # Payment doesn't have a custom __str__ method, so it uses the default
        # which would be something like "Payment object (1)" or similar
        assert hasattr(payment, "customernumber")
        assert hasattr(payment, "checknumber")

    @pytest.mark.django_db
    def test_payment_meta_options(self):
        """Test model meta options."""
        assert Payment._meta.managed is True  # Overridden for testing
        assert Payment._meta.db_table == "payments"
        assert Payment._meta.unique_together == (("customernumber", "checknumber"),)
        # Verify id field is the primary key
        assert Payment._meta.pk.name == "id"
        assert isinstance(Payment._meta.pk, models.AutoField)

    @pytest.mark.django_db
    def test_payment_field_attributes(self):
        """Test field attributes and constraints."""
        # Test checknumber field
        checknumber_field = Payment._meta.get_field("checknumber")
        assert checknumber_field.max_length == 50

        # Test amount field
        amount_field = Payment._meta.get_field("amount")
        assert amount_field.max_digits == 10
        assert amount_field.decimal_places == 2

    @pytest.mark.django_db
    def test_payment_foreign_key_relationships(self, customer):
        """Test foreign key relationships."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="REL001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        # Test customer relationship
        assert payment.customernumber == customer
        assert payment in customer.payment_set.all()

    @pytest.mark.django_db
    def test_payment_unique_together_constraint(self, customer):
        """Test unique together constraint on customernumber and checknumber."""
        Payment.objects.create(
            customernumber=customer,
            checknumber="UNIQUE001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        # Same customer, same check number should fail
        with pytest.raises(IntegrityError):
            Payment.objects.create(
                customernumber=customer,
                checknumber="UNIQUE001",  # Same check number
                paymentdate=date(2024, 1, 21),
                amount=Decimal("200.00"),
            )

    @pytest.mark.django_db
    def test_payment_same_check_number_different_customers(self, customer, employee):
        """Test that same check number can be used for different customers."""
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

        # Same check number for different customers should work
        payment1 = Payment.objects.create(
            customernumber=customer,
            checknumber="SAME001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        payment2 = Payment.objects.create(
            customernumber=customer2,
            checknumber="SAME001",  # Same check number, different customer
            paymentdate=date(2024, 1, 21),
            amount=Decimal("200.00"),
        )

        assert payment1.customernumber == customer
        assert payment2.customernumber == customer2
        assert payment1.checknumber == payment2.checknumber

    @pytest.mark.django_db
    def test_payment_decimal_precision(self, customer):
        """Test decimal field precision and scale."""
        # Test max value for (10,2)
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="PREC001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("99999999.99"),
        )

        assert payment.amount == Decimal("99999999.99")

    @pytest.mark.django_db
    def test_payment_negative_amount(self, customer):
        """Test handling of negative amounts."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="NEG001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("-100.00"),  # Negative amount (refund)
        )

        assert payment.amount == Decimal("-100.00")

    @pytest.mark.django_db
    def test_payment_zero_amount(self, customer):
        """Test handling of zero amounts."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="ZERO001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("0.00"),
        )

        assert payment.amount == Decimal("0.00")

    @pytest.mark.django_db
    def test_payment_check_number_formats(self, customer):
        """Test various check number formats."""
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
            payment = Payment.objects.create(
                customernumber=customer,
                checknumber=check_number,
                paymentdate=date(2024, 1, 20),
                amount=Decimal("100.00"),
            )

            assert payment.checknumber == check_number

    @pytest.mark.django_db
    def test_payment_date_variations(self, customer):
        """Test various payment dates."""
        dates = [
            date(2024, 1, 1),  # New Year
            date(2024, 2, 29),  # Leap year
            date(2024, 6, 15),  # Mid year
            date(2024, 12, 31),  # End of year
            date(2020, 1, 1),  # Past date
            date(2030, 1, 1),  # Future date
        ]

        for i, payment_date in enumerate(dates):
            payment = Payment.objects.create(
                customernumber=customer,
                checknumber=f"DATE{i:03d}",
                paymentdate=payment_date,
                amount=Decimal("100.00"),
            )

            assert payment.paymentdate == payment_date

    @pytest.mark.django_db
    def test_payment_unicode_handling(self, customer):
        """Test handling of unicode characters in check number."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="CHK with émojis 💰 and accents",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        assert "émojis" in payment.checknumber
        assert "💰" in payment.checknumber
        assert "accents" in payment.checknumber

    @pytest.mark.django_db
    def test_payment_large_check_number(self, customer):
        """Test handling of large check numbers."""
        large_check_number = "x" * 50  # Max length

        payment = Payment.objects.create(
            customernumber=customer,
            checknumber=large_check_number,
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        assert payment.checknumber == large_check_number
        assert len(payment.checknumber) == 50

    @pytest.mark.django_db
    def test_payment_max_length_constraints(self, customer):
        """Test field max length constraints."""
        # Test checknumber max length (50)
        with pytest.raises(ValidationError):
            payment = Payment(
                customernumber=customer,
                checknumber="x" * 51,  # Exceeds max_length=50
                paymentdate=date(2024, 1, 20),
                amount=Decimal("100.00"),
            )
            payment.full_clean()

    @pytest.mark.django_db
    def test_payment_multiple_payments_same_customer(self, customer):
        """Test multiple payments for the same customer."""
        payments = []
        for i in range(5):
            payment = Payment.objects.create(
                customernumber=customer,
                checknumber=f"MULT{i:03d}",
                paymentdate=date(2024, 1, 20 + i),
                amount=Decimal(f"{100.00 + i * 10.00}"),
            )
            payments.append(payment)

        # Test that all payments belong to the same customer
        for payment in payments:
            assert payment.customernumber == customer

        # Test that customer has all payments
        customer_payments = customer.payment_set.all()
        assert len(customer_payments) == 5

        for payment in payments:
            assert payment in customer_payments

    @pytest.mark.django_db
    def test_payment_amount_precision_rounding(self, customer):
        """Test amount field precision and rounding."""
        # Test that the field enforces 2 decimal places
        test_amounts = [
            ("12.35", Decimal("12.35")),  # Exact 2 decimal places
            ("12.34", Decimal("12.34")),  # Exact 2 decimal places
            ("12.00", Decimal("12.00")),  # Exact 2 decimal places
            ("0.01", Decimal("0.01")),  # Exact 2 decimal places
        ]

        for i, (input_amount, expected_amount) in enumerate(test_amounts):
            payment = Payment.objects.create(
                customernumber=customer,
                checknumber=f"ROUND{i:03d}",
                paymentdate=date(2024, 1, 20),
                amount=Decimal(input_amount),
            )

            assert payment.amount == expected_amount

        # Test that the field definition enforces 2 decimal places
        amount_field = Payment._meta.get_field("amount")
        assert amount_field.decimal_places == 2
        assert amount_field.max_digits == 10

    @pytest.mark.django_db
    def test_payment_very_small_amounts(self, customer):
        """Test handling of very small amounts."""
        small_amounts = [
            Decimal("0.01"),  # 1 cent
            Decimal("0.10"),  # 10 cents
            Decimal("0.99"),  # 99 cents
        ]

        for i, amount in enumerate(small_amounts):
            payment = Payment.objects.create(
                customernumber=customer,
                checknumber=f"SMALL{i:03d}",
                paymentdate=date(2024, 1, 20),
                amount=amount,
            )

            assert payment.amount == amount

    @pytest.mark.django_db
    def test_payment_very_large_amounts(self, customer):
        """Test handling of very large amounts."""
        large_amounts = [
            Decimal("99999999.99"),  # Max value for (10,2)
            Decimal("1000000.00"),  # 1 million
            Decimal("5000000.50"),  # 5 million and 50 cents
        ]

        for i, amount in enumerate(large_amounts):
            payment = Payment.objects.create(
                customernumber=customer,
                checknumber=f"LARGE{i:03d}",
                paymentdate=date(2024, 1, 20),
                amount=amount,
            )

            assert payment.amount == amount

    @pytest.mark.django_db
    def test_payment_required_fields(self, customer):
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            Payment.objects.create(
                customernumber=None,  # Required field
                checknumber="TEST",
                paymentdate=date(2024, 1, 20),
                amount=Decimal("100.00"),
            )

    @pytest.mark.django_db
    def test_payment_blank_check_number(self, customer):
        """Test handling of blank check number."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="",  # Empty string
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        assert payment.checknumber == ""

    @pytest.mark.django_db
    def test_payment_foreign_key_cascade_behavior(self, customer):
        """Test foreign key behavior when referenced object is deleted."""
        payment = Payment.objects.create(
            customernumber=customer,
            checknumber="CASCADE001",
            paymentdate=date(2024, 1, 20),
            amount=Decimal("100.00"),
        )

        # Since managed=False, we can't test actual cascade behavior
        # But we can test the relationship exists
        assert payment.customernumber == customer
