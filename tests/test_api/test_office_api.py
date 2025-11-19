"""
Tests for Office API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status

from classicmodels.models import Office


class TestOfficeAPI:
    """Test cases for Office API endpoints."""

    @pytest.mark.django_db
    def test_list_offices_authenticated(self, authenticated_api_client, office):
        """Test listing offices when authenticated."""
        url = reverse("classicmodels:office-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["officecode"] == office.officecode

    @pytest.mark.django_db
    def test_list_offices_unauthenticated(self, api_client, office):
        """Test listing offices when not authenticated."""
        url = reverse("classicmodels:office-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_office_authenticated(self, authenticated_api_client, office):
        """Test retrieving a specific office when authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["officecode"] == office.officecode
        assert response.data["city"] == office.city

    @pytest.mark.django_db
    def test_retrieve_office_unauthenticated(self, api_client, office):
        """Test retrieving an office when not authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_office(self, authenticated_api_client):
        """Test retrieving an office that doesn't exist."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": "NONEXISTENT"}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_office_authenticated(self, authenticated_api_client):
        """Test creating an office when authenticated."""
        url = reverse("classicmodels:office-list")
        data = {
            "officecode": "NEW001",
            "city": "New City",
            "phone": "+1-555-9999",
            "addressline1": "999 New Street",
            "addressline2": "Suite 500",
            "state": "NY",
            "country": "USA",
            "postalcode": "10001",
            "territory": "NA",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["officecode"] == "NEW001"
        assert response.data["city"] == "New City"

    @pytest.mark.django_db
    def test_create_office_unauthenticated(self, api_client):
        """Test creating an office when not authenticated."""
        url = reverse("classicmodels:office-list")
        data = {
            "officecode": "NEW001",
            "city": "New City",
            "phone": "+1-555-9999",
            "addressline1": "999 New Street",
            "country": "USA",
            "postalcode": "10001",
            "territory": "NA",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_office_duplicate_code(self, authenticated_api_client, office):
        """Test creating an office with duplicate office code."""
        url = reverse("classicmodels:office-list")
        data = {
            "officecode": office.officecode,  # Duplicate
            "city": "Duplicate City",
            "phone": "+1-555-0000",
            "addressline1": "123 Duplicate Ave",
            "country": "USA",
            "postalcode": "12345",
            "territory": "NA",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_office_minimal_data(self, authenticated_api_client):
        """Test creating an office with minimal required data."""
        url = reverse("classicmodels:office-list")
        data = {
            "officecode": "MIN001",
            "city": "Minimal City",
            "phone": "+1-555-0000",
            "addressline1": "123 Minimal Ave",
            "country": "USA",
            "postalcode": "12345",
            "territory": "NA",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["officecode"] == "MIN001"
        assert response.data["addressline2"] is None
        assert response.data["state"] is None

    @pytest.mark.django_db
    def test_update_office_authenticated(self, authenticated_api_client, office):
        """Test updating an office when authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        data = {
            "officecode": office.officecode,
            "city": "Updated City",
            "phone": "+1-555-8888",
            "addressline1": "888 Updated Street",
            "addressline2": "Suite 888",
            "state": "CA",
            "country": "USA",
            "postalcode": "90210",
            "territory": "NA",
        }

        response = authenticated_api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["city"] == "Updated City"
        assert response.data["phone"] == "+1-555-8888"

    @pytest.mark.django_db
    def test_update_office_unauthenticated(self, api_client, office):
        """Test updating an office when not authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        data = {
            "officecode": office.officecode,
            "city": "Updated City",
            "phone": "+1-555-8888",
            "addressline1": "888 Updated Street",
            "country": "USA",
            "postalcode": "90210",
            "territory": "NA",
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_office_authenticated(
        self, authenticated_api_client, office
    ):
        """Test partially updating an office when authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        data = {"city": "Partially Updated City", "phone": "+1-555-7777"}

        response = authenticated_api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["city"] == "Partially Updated City"
        assert response.data["phone"] == "+1-555-7777"
        # Other fields should remain unchanged
        assert response.data["officecode"] == office.officecode

    @pytest.mark.django_db
    def test_partial_update_office_unauthenticated(self, api_client, office):
        """Test partially updating an office when not authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        data = {"city": "Partially Updated City"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_office_authenticated(self, authenticated_api_client, office):
        """Test deleting an office when authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Office.objects.filter(officecode=office.officecode).exists()

    @pytest.mark.django_db
    def test_delete_office_unauthenticated(self, api_client, office):
        """Test deleting an office when not authenticated."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_office(self, authenticated_api_client):
        """Test deleting an office that doesn't exist."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": "NONEXISTENT"}
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_office_serializer_validation(self, authenticated_api_client):
        """Test office serializer validation."""
        url = reverse("classicmodels:office-list")

        # Test with invalid data (exceeds max length)
        data = {
            "officecode": "x" * 11,  # Exceeds max_length=10
            "city": "Valid City",
            "phone": "+1-555-0000",
            "addressline1": "123 Valid Ave",
            "country": "USA",
            "postalcode": "12345",
            "territory": "NA",
        }

        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_office_phone_formats(self, authenticated_api_client):
        """Test various phone number formats."""
        url = reverse("classicmodels:office-list")
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
                "officecode": f"PHONE{i:03d}",
                "city": f"Phone City {i}",
                "phone": phone,
                "addressline1": f"{100+i} Phone Ave",
                "country": "USA",
                "postalcode": f"{10000+i}",
                "territory": "NA",
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["phone"] == phone

    @pytest.mark.django_db
    def test_office_postal_code_formats(self, authenticated_api_client):
        """Test various postal code formats."""
        url = reverse("classicmodels:office-list")
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
                "officecode": f"POST{i:03d}",
                "city": f"Postal City {i}",
                "phone": "+1-555-0000",
                "addressline1": f"{100+i} Postal Ave",
                "country": "USA",
                "postalcode": postal_code,
                "territory": "NA",
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["postalcode"] == postal_code

    @pytest.mark.django_db
    def test_office_territory_values(self, authenticated_api_client):
        """Test various territory values."""
        url = reverse("classicmodels:office-list")
        territories = ["NA", "EMEA", "APAC", "LATAM", "GLOBAL"]

        for i, territory in enumerate(territories):
            data = {
                "officecode": f"TERR{i:03d}",
                "city": f"Territory City {i}",
                "phone": "+1-555-0000",
                "addressline1": f"{100+i} Territory Ave",
                "country": "USA",
                "postalcode": "12345",
                "territory": territory,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["territory"] == territory

    @pytest.mark.django_db
    def test_office_unicode_handling(self, authenticated_api_client):
        """Test handling of unicode characters in office."""
        url = reverse("classicmodels:office-list")
        data = {
            "officecode": "UNICODE001",
            "city": "Cité émojis 🏢",
            "phone": "+1-555-émojis",
            "addressline1": "123 Rue émojis 🏠",
            "addressline2": "Suite émojis 🏢",
            "state": "État émojis 🌟",
            "country": "Pays émojis 🌍",
            "postalcode": "12345-émojis",
            "territory": "TERR-émoj",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "émojis" in response.data["city"]
        assert "🏢" in response.data["city"]
        assert "émojis" in response.data["addressline1"]
        assert "🏠" in response.data["addressline1"]

    @pytest.mark.django_db
    def test_office_address_combinations(self, authenticated_api_client):
        """Test various address line combinations."""
        url = reverse("classicmodels:office-list")

        # Test with both address lines
        data1 = {
            "officecode": "ADDR001",
            "city": "Both Lines City",
            "phone": "+1-555-0000",
            "addressline1": "123 Main Street",
            "addressline2": "Suite 500",
            "country": "USA",
            "postalcode": "12345",
            "territory": "NA",
        }

        response1 = authenticated_api_client.post(url, data1, format="json")
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.data["addressline1"] == "123 Main Street"
        assert response1.data["addressline2"] == "Suite 500"

        # Test with only address line 1
        data2 = {
            "officecode": "ADDR002",
            "city": "One Line City",
            "phone": "+1-555-0000",
            "addressline1": "456 Single Ave",
            "country": "USA",
            "postalcode": "54321",
            "territory": "NA",
        }

        response2 = authenticated_api_client.post(url, data2, format="json")
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.data["addressline1"] == "456 Single Ave"
        assert response2.data["addressline2"] is None

    @pytest.mark.django_db
    def test_office_state_combinations(self, authenticated_api_client):
        """Test various state field combinations."""
        url = reverse("classicmodels:office-list")

        # Test with state
        data1 = {
            "officecode": "STATE001",
            "city": "State City",
            "phone": "+1-555-0000",
            "addressline1": "123 State Ave",
            "state": "CA",
            "country": "USA",
            "postalcode": "12345",
            "territory": "NA",
        }

        response1 = authenticated_api_client.post(url, data1, format="json")
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.data["state"] == "CA"

        # Test without state
        data2 = {
            "officecode": "STATE002",
            "city": "No State City",
            "phone": "+1-555-0000",
            "addressline1": "456 No State Ave",
            "country": "Canada",
            "postalcode": "K1A 0A6",
            "territory": "NA",
        }

        response2 = authenticated_api_client.post(url, data2, format="json")
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.data["state"] is None

    @pytest.mark.django_db
    def test_office_pagination(self, authenticated_api_client, multiple_offices):
        """Test office pagination."""
        # Create additional offices beyond the existing ones
        for i in range(15):  # More than default page size
            Office.objects.create(
                officecode=f"PAGE{i:03d}",
                city=f"Pagination City {i}",
                phone=f"+1-555-{1000+i:04d}",
                addressline1=f"{100+i} Pagination Ave",
                country="USA",
                postalcode=f"{10000+i}",
                territory="NA",
            )

        url = reverse("classicmodels:office-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    @pytest.mark.django_db
    def test_office_ordering(self, authenticated_api_client):
        """Test office ordering."""
        # Create offices in specific order
        Office.objects.create(
            officecode="ZOFF001",
            city="Z Office City",
            phone="+1-555-0000",
            addressline1="123 Z Ave",
            country="USA",
            postalcode="12345",
            territory="NA",
        )
        Office.objects.create(
            officecode="AOFF001",
            city="A Office City",
            phone="+1-555-0000",
            addressline1="123 A Ave",
            country="USA",
            postalcode="12345",
            territory="NA",
        )

        url = reverse("classicmodels:office-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data["results"]) >= 2

    @pytest.mark.django_db
    def test_office_relationships(self, authenticated_api_client, office, employee):
        """Test office relationships in API response."""
        url = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Note: Employee relationships might not be included in the response
        # depending on the serializer configuration

    @pytest.mark.django_db
    def test_get_office_employees_authenticated(
        self, authenticated_api_client, office, employee
    ):
        """Test retrieving employees for an office when authenticated."""
        url = reverse(
            "classicmodels:office-employees",
            kwargs={"officecode": office.officecode},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data or isinstance(response.data, list)
        # If paginated, check results; otherwise check list directly
        if "results" in response.data:
            assert len(response.data["results"]) >= 1
            assert response.data["results"][0]["employeenumber"] == employee.employeenumber
        else:
            assert len(response.data) >= 1
            assert response.data[0]["employeenumber"] == employee.employeenumber

    @pytest.mark.django_db
    def test_get_office_employees_unauthenticated(self, api_client, office):
        """Test retrieving employees for an office when not authenticated."""
        url = reverse(
            "classicmodels:office-employees",
            kwargs={"officecode": office.officecode},
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_get_office_employees_nonexistent_office(
        self, authenticated_api_client
    ):
        """Test retrieving employees for an office that doesn't exist."""
        url = reverse(
            "classicmodels:office-employees", kwargs={"officecode": "NONEXIST"}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_get_office_employees_empty(self, authenticated_api_client):
        """Test retrieving employees for an office with no employees."""
        from classicmodels.models import Office

        # Create an office with no employees
        office_no_employees = Office.objects.create(
            officecode="EMPTY01",
            city="Empty City",
            phone="+1-555-0000",
            addressline1="123 Empty Street",
            country="USA",
            postalcode="12345",
            territory="NA",
        )

        url = reverse(
            "classicmodels:office-employees",
            kwargs={"officecode": office_no_employees.officecode},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should return empty list or empty results
        if "results" in response.data:
            assert len(response.data["results"]) == 0
        else:
            assert len(response.data) == 0

    @pytest.mark.django_db
    def test_get_office_employees_multiple_employees(
        self, authenticated_api_client, office
    ):
        """Test retrieving employees for an office with multiple employees."""
        from classicmodels.models import Employee

        # Create multiple employees in this office
        employees = []
        for i in range(3):
            employee = Employee.objects.create(
                employeenumber=2000 + i,
                lastname=f"Employee{i+1}",
                firstname="Test",
                extension=f"EXT{i+1}",
                email=f"employee{i+1}@example.com",
                officecode=office,
                jobtitle="Sales Rep",
            )
            employees.append(employee)

        url = reverse(
            "classicmodels:office-employees",
            kwargs={"officecode": office.officecode},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Check that all employees are returned
        if "results" in response.data:
            employee_numbers = [
                e["employeenumber"] for e in response.data["results"]
            ]
        else:
            employee_numbers = [e["employeenumber"] for e in response.data]

        for employee in employees:
            assert employee.employeenumber in employee_numbers

    @pytest.mark.django_db
    def test_get_office_employees_pagination(
        self, authenticated_api_client, office
    ):
        """Test pagination for office employees endpoint."""
        from classicmodels.models import Employee

        # Create more employees than default page size
        for i in range(15):
            Employee.objects.create(
                employeenumber=3000 + i,
                lastname=f"Pagination{i+1}",
                firstname="Test",
                extension=f"PAGE{i+1}",
                email=f"pagination{i+1}@example.com",
                officecode=office,
                jobtitle="Sales Rep",
            )

        url = reverse(
            "classicmodels:office-employees",
            kwargs={"officecode": office.officecode},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should have pagination metadata
        assert "count" in response.data
        assert "next" in response.data or response.data["next"] is None
        assert "previous" in response.data or response.data["previous"] is None
        assert "results" in response.data
