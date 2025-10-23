"""
Tests for Customer model.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from classicmodels.models import Customer


class TestCustomerModel:
    """Test cases for Customer model."""

    @pytest.mark.django_db
    def test_customer_creation(self, employee):
        """Test creating a customer with all fields."""
        customer = Customer.objects.create(
            customernumber=1001,
            customername="Test Customer Inc.",
            contactlastname="Johnson",
            contactfirstname="Bob",
            phone="+1-555-0456",
            addressline1="456 Customer Ave",
            addressline2="Suite 200",
            city="Customer City",
            state="CA",
            postalcode="90210",
            country="USA",
            salesrepemployeenumber=employee,
            creditlimit=Decimal("50000.00"),
        )

        assert customer.customernumber == 1001
        assert customer.customername == "Test Customer Inc."
        assert customer.contactlastname == "Johnson"
        assert customer.contactfirstname == "Bob"
        assert customer.phone == "+1-555-0456"
        assert customer.addressline1 == "456 Customer Ave"
        assert customer.addressline2 == "Suite 200"
        assert customer.city == "Customer City"
        assert customer.state == "CA"
        assert customer.postalcode == "90210"
        assert customer.country == "USA"
        assert customer.salesrepemployeenumber == employee
        assert customer.creditlimit == Decimal("50000.00")

    @pytest.mark.django_db
    def test_customer_creation_minimal(self, employee):
        """Test creating a customer with only required fields."""
        customer = Customer.objects.create(
            customernumber=1002,
            customername="Minimal Customer",
            contactlastname="Smith",
            contactfirstname="Jane",
            phone="+1-555-0000",
            addressline1="123 Minimal Ave",
            city="Minimal City",
            country="USA",
            salesrepemployeenumber=employee,
        )

        assert customer.customernumber == 1002
        assert customer.customername == "Minimal Customer"
        assert customer.contactlastname == "Smith"
        assert customer.contactfirstname == "Jane"
        assert customer.phone == "+1-555-0000"
        assert customer.addressline1 == "123 Minimal Ave"
        assert customer.city == "Minimal City"
        assert customer.country == "USA"
        assert customer.salesrepemployeenumber == employee
        assert customer.addressline2 is None
        assert customer.state is None
        assert customer.postalcode is None
        assert customer.creditlimit is None

    @pytest.mark.django_db
    def test_customer_string_representation(self, employee):
        """Test the string representation of Customer."""
        customer = Customer.objects.create(
            customernumber=1003,
            customername="Representation Customer",
            contactlastname="Wilson",
            contactfirstname="Alice",
            phone="+1-555-0000",
            addressline1="789 Rep Ave",
            city="Rep City",
            country="USA",
            salesrepemployeenumber=employee,
        )

        assert str(customer) == "1003"

    @pytest.mark.django_db
    def test_customer_primary_key(self, employee):
        """Test that customernumber is the primary key."""
        customer = Customer.objects.create(
            customernumber=1004,
            customername="PK Customer",
            contactlastname="Brown",
            contactfirstname="Charlie",
            phone="+1-555-0000",
            addressline1="123 PK Ave",
            city="PK City",
            country="USA",
            salesrepemployeenumber=employee,
        )

        assert customer.pk == 1004

    @pytest.mark.django_db
    def test_customer_max_length_constraints(self, employee):
        """Test field max length constraints."""
        # Test customername max length (50)
        with pytest.raises(ValidationError):
            customer = Customer(
                customernumber=1005,
                customername="x" * 51,  # Exceeds max_length=50
                contactlastname="Test",
                contactfirstname="Test",
                phone="+1-555-0000",
                addressline1="123 Test Ave",
                city="Test City",
                country="USA",
                salesrepemployeenumber=employee,
            )
            customer.full_clean()

        # Test contactlastname max length (50)
        with pytest.raises(ValidationError):
            customer = Customer(
                customernumber=1006,
                customername="Test",
                contactlastname="x" * 51,  # Exceeds max_length=50
                contactfirstname="Test",
                phone="+1-555-0000",
                addressline1="123 Test Ave",
                city="Test City",
                country="USA",
                salesrepemployeenumber=employee,
            )
            customer.full_clean()

    @pytest.mark.django_db
    def test_customer_blank_fields(self, employee):
        """Test that optional fields can be blank."""
        customer = Customer.objects.create(
            customernumber=1007,
            customername="Blank Customer",
            contactlastname="Blank",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Blank Ave",
            addressline2="",  # Empty string should be allowed
            city="Blank City",
            state="",  # Empty string should be allowed
            postalcode="",  # Empty string should be allowed
            country="USA",
            salesrepemployeenumber=employee,
        )

        assert customer.addressline2 == ""
        assert customer.state == ""
        assert customer.postalcode == ""

    @pytest.mark.django_db
    def test_customer_null_fields(self, employee):
        """Test that optional fields can be null."""
        customer = Customer.objects.create(
            customernumber=1008,
            customername="Null Customer",
            contactlastname="Null",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Null Ave",
            addressline2=None,
            city="Null City",
            state=None,
            postalcode=None,
            country="USA",
            salesrepemployeenumber=employee,
            creditlimit=None,
        )

        assert customer.addressline2 is None
        assert customer.state is None
        assert customer.postalcode is None
        assert customer.creditlimit is None

    @pytest.mark.django_db
    def test_customer_unique_constraint(self, employee):
        """Test that customernumber must be unique."""
        Customer.objects.create(
            customernumber=1009,
            customername="Unique Customer",
            contactlastname="Unique",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Unique Ave",
            city="Unique City",
            country="USA",
            salesrepemployeenumber=employee,
        )

        with pytest.raises(IntegrityError):
            Customer.objects.create(
                customernumber=1009,  # Duplicate
                customername="Another Customer",
                contactlastname="Another",
                contactfirstname="Test",
                phone="+1-555-0000",
                addressline1="456 Another Ave",
                city="Another City",
                country="USA",
                salesrepemployeenumber=employee,
            )

    @pytest.mark.django_db
    def test_customer_meta_options(self):
        """Test model meta options."""
        assert Customer._meta.managed is True  # Overridden for testing
        assert Customer._meta.db_table == "customers"

    @pytest.mark.django_db
    def test_customer_field_attributes(self):
        """Test field attributes and constraints."""
        # Test customernumber field
        customernumber_field = Customer._meta.get_field("customernumber")
        assert customernumber_field.primary_key is True

        # Test customername field
        customername_field = Customer._meta.get_field("customername")
        assert customername_field.max_length == 50

        # Test contactlastname field
        contactlastname_field = Customer._meta.get_field("contactlastname")
        assert contactlastname_field.max_length == 50

        # Test contactfirstname field
        contactfirstname_field = Customer._meta.get_field("contactfirstname")
        assert contactfirstname_field.max_length == 50

        # Test phone field
        phone_field = Customer._meta.get_field("phone")
        assert phone_field.max_length == 50

        # Test addressline1 field
        addressline1_field = Customer._meta.get_field("addressline1")
        assert addressline1_field.max_length == 50

        # Test addressline2 field
        addressline2_field = Customer._meta.get_field("addressline2")
        assert addressline2_field.max_length == 50
        assert addressline2_field.blank is True
        assert addressline2_field.null is True

        # Test city field
        city_field = Customer._meta.get_field("city")
        assert city_field.max_length == 50

        # Test state field
        state_field = Customer._meta.get_field("state")
        assert state_field.max_length == 50
        assert state_field.blank is True
        assert state_field.null is True

        # Test postalcode field
        postalcode_field = Customer._meta.get_field("postalcode")
        assert postalcode_field.max_length == 15
        assert postalcode_field.blank is True
        assert postalcode_field.null is True

        # Test country field
        country_field = Customer._meta.get_field("country")
        assert country_field.max_length == 50

        # Test creditlimit field
        creditlimit_field = Customer._meta.get_field("creditlimit")
        assert creditlimit_field.max_digits == 10
        assert creditlimit_field.decimal_places == 2
        assert creditlimit_field.blank is True
        assert creditlimit_field.null is True

    @pytest.mark.django_db
    def test_customer_foreign_key_relationships(self, employee):
        """Test foreign key relationships."""
        customer = Customer.objects.create(
            customernumber=1010,
            customername="Relationship Customer",
            contactlastname="Relationship",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Relationship Ave",
            city="Relationship City",
            country="USA",
            salesrepemployeenumber=employee,
        )

        # Test sales rep relationship
        assert customer.salesrepemployeenumber == employee
        assert customer in employee.customer_set.all()

    @pytest.mark.django_db
    def test_customer_credit_limit_precision(self, employee):
        """Test credit limit decimal precision."""
        customer = Customer.objects.create(
            customernumber=1011,
            customername="Credit Customer",
            contactlastname="Credit",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Credit Ave",
            city="Credit City",
            country="USA",
            salesrepemployeenumber=employee,
            creditlimit=Decimal("99999999.99"),  # Max value for (10,2)
        )

        assert customer.creditlimit == Decimal("99999999.99")

    @pytest.mark.django_db
    def test_customer_phone_formats(self, employee):
        """Test various phone number formats."""
        phone_formats = [
            "+1-555-0123",
            "(555) 123-4567",
            "555-123-4567",
            "5551234567",
            "+44 20 7946 0958",
            "+33 1 42 86 83 26",
        ]

        for i, phone in enumerate(phone_formats):
            customer = Customer.objects.create(
                customernumber=1020 + i,
                customername=f"Phone Customer {i}",
                contactlastname=f"Phone{i}",
                contactfirstname="Test",
                phone=phone,
                addressline1=f"{100+i} Phone Ave",
                city=f"Phone City {i}",
                country="USA",
                salesrepemployeenumber=employee,
            )

            assert customer.phone == phone

    @pytest.mark.django_db
    def test_customer_postal_code_formats(self, employee):
        """Test various postal code formats."""
        postal_codes = [
            "12345",  # US ZIP
            "12345-6789",  # US ZIP+4
            "K1A 0A6",  # Canadian postal code
            "SW1A 1AA",  # UK postal code
            "75001",  # French postal code
            "100-0001",  # Japanese postal code
        ]

        for i, postal_code in enumerate(postal_codes):
            customer = Customer.objects.create(
                customernumber=1030 + i,
                customername=f"Postal Customer {i}",
                contactlastname=f"Postal{i}",
                contactfirstname="Test",
                phone="+1-555-0000",
                addressline1=f"{100+i} Postal Ave",
                city=f"Postal City {i}",
                postalcode=postal_code,
                country="USA",
                salesrepemployeenumber=employee,
            )

            assert customer.postalcode == postal_code

    @pytest.mark.django_db
    def test_customer_unicode_handling(self, employee):
        """Test handling of unicode characters."""
        customer = Customer.objects.create(
            customernumber=1040,
            customername="Customer with émojis 🏢 and accents",
            contactlastname="Doe with émojis 👤 and accents",
            contactfirstname="Jean with émojis 👨 and accents",
            phone="+1-555-émojis",
            addressline1="123 Rue de la Paix with émojis 🏠",
            addressline2="Suite 100 with émojis 🏢",
            city="Cité with émojis 🌆 and accents",
            state="État with émojis 🌟",
            postalcode="12345-émojis",
            country="Pays with émojis 🌍",
            salesrepemployeenumber=employee,
            creditlimit=Decimal("50000.00"),
        )

        assert "émojis" in customer.customername
        assert "🏢" in customer.customername
        assert "émojis" in customer.contactlastname
        assert "👤" in customer.contactlastname
        assert "émojis" in customer.contactfirstname
        assert "👨" in customer.contactfirstname

    @pytest.mark.django_db
    def test_customer_negative_credit_limit(self, employee):
        """Test handling of negative credit limit."""
        customer = Customer.objects.create(
            customernumber=1050,
            customername="Negative Credit Customer",
            contactlastname="Negative",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Negative Ave",
            city="Negative City",
            country="USA",
            salesrepemployeenumber=employee,
            creditlimit=Decimal("-1000.00"),  # Negative credit limit
        )

        assert customer.creditlimit == Decimal("-1000.00")

    @pytest.mark.django_db
    def test_customer_zero_credit_limit(self, employee):
        """Test handling of zero credit limit."""
        customer = Customer.objects.create(
            customernumber=1051,
            customername="Zero Credit Customer",
            contactlastname="Zero",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Zero Ave",
            city="Zero City",
            country="USA",
            salesrepemployeenumber=employee,
            creditlimit=Decimal("0.00"),
        )

        assert customer.creditlimit == Decimal("0.00")

    @pytest.mark.django_db
    def test_customer_large_credit_limit(self, employee):
        """Test handling of large credit limit."""
        large_credit = Decimal("99999999.99")  # Max value for (10,2)

        customer = Customer.objects.create(
            customernumber=1052,
            customername="Large Credit Customer",
            contactlastname="Large",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Large Ave",
            city="Large City",
            country="USA",
            salesrepemployeenumber=employee,
            creditlimit=large_credit,
        )

        assert customer.creditlimit == large_credit

    @pytest.mark.django_db
    def test_customer_without_sales_rep(self):
        """Test customer without sales rep."""
        customer = Customer.objects.create(
            customernumber=1053,
            customername="No Rep Customer",
            contactlastname="NoRep",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 NoRep Ave",
            city="NoRep City",
            country="USA",
            salesrepemployeenumber=None,
        )

        assert customer.salesrepemployeenumber is None

    @pytest.mark.django_db
    def test_customer_address_combinations(self, employee):
        """Test various address line combinations."""
        # Test with both address lines
        customer1 = Customer.objects.create(
            customernumber=1060,
            customername="Both Lines Customer",
            contactlastname="Both",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 Main Street",
            addressline2="Suite 500",
            city="Both City",
            country="USA",
            salesrepemployeenumber=employee,
        )
        assert customer1.addressline1 == "123 Main Street"
        assert customer1.addressline2 == "Suite 500"

        # Test with only address line 1
        customer2 = Customer.objects.create(
            customernumber=1061,
            customername="One Line Customer",
            contactlastname="One",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="456 Single Ave",
            city="One City",
            country="USA",
            salesrepemployeenumber=employee,
        )
        assert customer2.addressline1 == "456 Single Ave"
        assert customer2.addressline2 is None

    @pytest.mark.django_db
    def test_customer_state_combinations(self, employee):
        """Test various state field combinations."""
        # Test with state
        customer1 = Customer.objects.create(
            customernumber=1070,
            customername="State Customer",
            contactlastname="State",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="123 State Ave",
            city="State City",
            state="CA",
            country="USA",
            salesrepemployeenumber=employee,
        )
        assert customer1.state == "CA"

        # Test without state
        customer2 = Customer.objects.create(
            customernumber=1071,
            customername="No State Customer",
            contactlastname="NoState",
            contactfirstname="Test",
            phone="+1-555-0000",
            addressline1="456 No State Ave",
            city="No State City",
            country="Canada",
            salesrepemployeenumber=employee,
        )
        assert customer2.state is None
