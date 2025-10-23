"""
Tests for Office model.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from classicmodels.models import Office


class TestOfficeModel:
    """Test cases for Office model."""

    @pytest.mark.django_db
    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_creation(self):
        """Test creating an office with all fields."""
        office = Office.objects.create(
            officecode="TEST001",
            city="Test City",
            phone="+1-555-0123",
            addressline1="123 Test Street",
            addressline2="Suite 100",
            state="CA",
            country="USA",
            postalcode="12345",
            territory="NA",
        )

        assert office.officecode == "TEST001"
        assert office.city == "Test City"
        assert office.phone == "+1-555-0123"
        assert office.addressline1 == "123 Test Street"
        assert office.addressline2 == "Suite 100"
        assert office.state == "CA"
        assert office.country == "USA"
        assert office.postalcode == "12345"
        assert office.territory == "NA"

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_creation_minimal(self):
        """Test creating an office with only required fields."""
        office = Office.objects.create(
            officecode="MIN001",
            city="Minimal City",
            phone="+1-555-0000",
            addressline1="456 Minimal Ave",
            country="USA",
            postalcode="54321",
            territory="NA",
        )

        assert office.officecode == "MIN001"
        assert office.city == "Minimal City"
        assert office.phone == "+1-555-0000"
        assert office.addressline1 == "456 Minimal Ave"
        assert office.country == "USA"
        assert office.postalcode == "54321"
        assert office.territory == "NA"
        assert office.addressline2 is None
        assert office.state is None

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_string_representation(self):
        """Test the string representation of Office."""
        office = Office.objects.create(
            officecode="REPR001",
            city="Representation City",
            phone="+1-555-0000",
            addressline1="789 Rep Ave",
            country="USA",
            postalcode="98765",
            territory="NA",
        )

        assert str(office) == "REPR001"

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_primary_key(self):
        """Test that officecode is the primary key."""
        office = Office.objects.create(
            officecode="PK001",
            city="PK City",
            phone="+1-555-0000",
            addressline1="123 PK Ave",
            country="USA",
            postalcode="11111",
            territory="NA",
        )

        assert office.pk == "PK001"

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_max_length_constraints(self):
        """Test field max length constraints."""
        # Test officecode max length (10)
        with pytest.raises(ValidationError):
            office = Office(
                officecode="x" * 11,  # Exceeds max_length=10
                city="Test",
                phone="+1-555-0000",
                addressline1="123 Test Ave",
                country="USA",
                postalcode="12345",
                territory="NA",
            )
            office.full_clean()

        # Test city max length (50)
        with pytest.raises(ValidationError):
            office = Office(
                officecode="TEST",
                city="x" * 51,  # Exceeds max_length=50
                phone="+1-555-0000",
                addressline1="123 Test Ave",
                country="USA",
                postalcode="12345",
                territory="NA",
            )
            office.full_clean()

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_blank_fields(self):
        """Test that optional fields can be blank."""
        office = Office.objects.create(
            officecode="BLANK001",
            city="Blank City",
            phone="+1-555-0000",
            addressline1="123 Blank Ave",
            addressline2="",  # Empty string should be allowed
            state="",  # Empty string should be allowed
            country="USA",
            postalcode="12345",
            territory="NA",
        )

        assert office.addressline2 == ""
        assert office.state == ""

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_null_fields(self):
        """Test that optional fields can be null."""
        office = Office.objects.create(
            officecode="NULL001",
            city="Null City",
            phone="+1-555-0000",
            addressline1="123 Null Ave",
            addressline2=None,
            state=None,
            country="USA",
            postalcode="12345",
            territory="NA",
        )

        assert office.addressline2 is None
        assert office.state is None

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_unique_constraint(self):
        """Test that officecode must be unique."""
        Office.objects.create(
            officecode="UNIQUE001",
            city="Unique City",
            phone="+1-555-0000",
            addressline1="123 Unique Ave",
            country="USA",
            postalcode="12345",
            territory="NA",
        )

        with pytest.raises(IntegrityError):
            Office.objects.create(
                officecode="UNIQUE001",  # Duplicate
                city="Another City",
                phone="+1-555-0000",
                addressline1="456 Another Ave",
                country="USA",
                postalcode="54321",
                territory="NA",
            )

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_meta_options(self):
        """Test model meta options."""
        assert Office._meta.managed is True  # Overridden for testing
        assert Office._meta.db_table == "offices"

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_field_attributes(self):
        """Test field attributes and constraints."""
        # Test officecode field
        officecode_field = Office._meta.get_field("officecode")
        assert officecode_field.max_length == 10
        assert officecode_field.primary_key is True

        # Test city field
        city_field = Office._meta.get_field("city")
        assert city_field.max_length == 50

        # Test phone field
        phone_field = Office._meta.get_field("phone")
        assert phone_field.max_length == 50

        # Test addressline1 field
        addressline1_field = Office._meta.get_field("addressline1")
        assert addressline1_field.max_length == 50

        # Test addressline2 field
        addressline2_field = Office._meta.get_field("addressline2")
        assert addressline2_field.max_length == 50
        assert addressline2_field.blank is True
        assert addressline2_field.null is True

        # Test state field
        state_field = Office._meta.get_field("state")
        assert state_field.max_length == 50
        assert state_field.blank is True
        assert state_field.null is True

        # Test country field
        country_field = Office._meta.get_field("country")
        assert country_field.max_length == 50

        # Test postalcode field
        postalcode_field = Office._meta.get_field("postalcode")
        assert postalcode_field.max_length == 15

        # Test territory field
        territory_field = Office._meta.get_field("territory")
        assert territory_field.max_length == 10

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_relationships(self, office, employee):
        """Test relationships with other models."""
        # Test reverse relationship with Employee
        assert employee.officecode == office
        assert employee in office.employee_set.all()

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_phone_formats(self):
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
            office = Office.objects.create(
                officecode=f"PHONE{i:03d}",
                city=f"Phone City {i}",
                phone=phone,
                addressline1=f"{100+i} Phone Ave",
                country="USA",
                postalcode=f"{10000+i}",
                territory="NA",
            )

            assert office.phone == phone

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_postal_code_formats(self):
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
            office = Office.objects.create(
                officecode=f"POST{i:03d}",
                city=f"Postal City {i}",
                phone="+1-555-0000",
                addressline1=f"{100+i} Postal Ave",
                country="USA",
                postalcode=postal_code,
                territory="NA",
            )

            assert office.postalcode == postal_code

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_territory_values(self):
        """Test various territory values."""
        territories = ["NA", "EMEA", "APAC", "LATAM", "GLOBAL"]

        for i, territory in enumerate(territories):
            office = Office.objects.create(
                officecode=f"TERR{i:03d}",
                city=f"Territory City {i}",
                phone="+1-555-0000",
                addressline1=f"{100+i} Territory Ave",
                country="USA",
                postalcode="12345",
                territory=territory,
            )

            assert office.territory == territory

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_unicode_handling(self):
        """Test handling of unicode characters."""
        office = Office.objects.create(
            officecode="UNICODE001",
            city="Cité with émojis 🏢 and accents",
            phone="+1-555-émojis",
            addressline1="123 Rue de la Paix with émojis 🏠",
            addressline2="Suite 100 with émojis 🏢",
            state="État with émojis 🌟",
            country="Pays with émojis 🌍",
            postalcode="12345-émojis",
            territory="TERR-émojis",
        )

        assert "émojis" in office.city
        assert "🏢" in office.city
        assert "émojis" in office.addressline1
        assert "🏠" in office.addressline1

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_address_combinations(self):
        """Test various address line combinations."""
        # Test with both address lines
        office1 = Office.objects.create(
            officecode="ADDR001",
            city="Both Lines City",
            phone="+1-555-0000",
            addressline1="123 Main Street",
            addressline2="Suite 500",
            country="USA",
            postalcode="12345",
            territory="NA",
        )
        assert office1.addressline1 == "123 Main Street"
        assert office1.addressline2 == "Suite 500"

        # Test with only address line 1
        office2 = Office.objects.create(
            officecode="ADDR002",
            city="One Line City",
            phone="+1-555-0000",
            addressline1="456 Single Ave",
            country="USA",
            postalcode="54321",
            territory="NA",
        )
        assert office2.addressline1 == "456 Single Ave"
        assert office2.addressline2 is None

    @pytest.mark.django_db
    @pytest.mark.django_db
    def test_office_state_combinations(self):
        """Test various state field combinations."""
        # Test with state
        office1 = Office.objects.create(
            officecode="STATE001",
            city="State City",
            phone="+1-555-0000",
            addressline1="123 State Ave",
            state="CA",
            country="USA",
            postalcode="12345",
            territory="NA",
        )
        assert office1.state == "CA"

        # Test without state
        office2 = Office.objects.create(
            officecode="STATE002",
            city="No State City",
            phone="+1-555-0000",
            addressline1="456 No State Ave",
            country="Canada",
            postalcode="K1A 0A6",
            territory="NA",
        )
        assert office2.state is None
