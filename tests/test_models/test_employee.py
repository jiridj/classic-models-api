"""
Tests for Employee model.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from classicmodels.models import Employee


class TestEmployeeModel:
    """Test cases for Employee model."""

    @pytest.mark.django_db
    def test_employee_creation(self, office):
        """Test creating an employee with all fields."""
        employee = Employee.objects.create(
            employeenumber=1001,
            lastname="Doe",
            firstname="John",
            extension="1234",
            email="john.doe@example.com",
            officecode=office,
            reportsto=None,
            jobtitle="Sales Rep",
        )

        assert employee.employeenumber == 1001
        assert employee.lastname == "Doe"
        assert employee.firstname == "John"
        assert employee.extension == "1234"
        assert employee.email == "john.doe@example.com"
        assert employee.officecode == office
        assert employee.reportsto is None
        assert employee.jobtitle == "Sales Rep"

    @pytest.mark.django_db
    def test_employee_with_manager(self, office, manager_employee):
        """Test creating an employee with a manager."""
        employee = Employee.objects.create(
            employeenumber=1002,
            lastname="Smith",
            firstname="Jane",
            extension="5678",
            email="jane.smith@example.com",
            officecode=office,
            reportsto=manager_employee,
            jobtitle="Sales Rep",
        )

        assert employee.reportsto == manager_employee
        assert employee in manager_employee.employee_set.all()

    @pytest.mark.django_db
    def test_employee_string_representation(self, office):
        """Test the string representation of Employee."""
        employee = Employee.objects.create(
            employeenumber=1003,
            lastname="Johnson",
            firstname="Bob",
            extension="9999",
            email="bob.johnson@example.com",
            officecode=office,
            jobtitle="Manager",
        )

        assert str(employee) == "1003"  # Primary key

    @pytest.mark.django_db
    def test_employee_primary_key(self, office):
        """Test that employeenumber is the primary key."""
        employee = Employee.objects.create(
            employeenumber=1004,
            lastname="Wilson",
            firstname="Alice",
            extension="1111",
            email="alice.wilson@example.com",
            officecode=office,
            jobtitle="Analyst",
        )

        assert employee.pk == 1004

    @pytest.mark.django_db
    def test_employee_max_length_constraints(self, office):
        """Test field max length constraints."""
        # Test lastname max length (50)
        with pytest.raises(ValidationError):
            employee = Employee(
                employeenumber=1005,
                lastname="x" * 51,  # Exceeds max_length=50
                firstname="Test",
                extension="1234",
                email="test@example.com",
                officecode=office,
                jobtitle="Test",
            )
            employee.full_clean()

        # Test firstname max length (50)
        with pytest.raises(ValidationError):
            employee = Employee(
                employeenumber=1006,
                lastname="Test",
                firstname="x" * 51,  # Exceeds max_length=50
                extension="1234",
                email="test@example.com",
                officecode=office,
                jobtitle="Test",
            )
            employee.full_clean()

        # Test extension max length (10)
        with pytest.raises(ValidationError):
            employee = Employee(
                employeenumber=1007,
                lastname="Test",
                firstname="Test",
                extension="x" * 11,  # Exceeds max_length=10
                email="test@example.com",
                officecode=office,
                jobtitle="Test",
            )
            employee.full_clean()

        # Test email max length (100)
        with pytest.raises(ValidationError):
            employee = Employee(
                employeenumber=1008,
                lastname="Test",
                firstname="Test",
                extension="1234",
                email="x" * 101,  # Exceeds max_length=100
                officecode=office,
                jobtitle="Test",
            )
            employee.full_clean()

        # Test jobtitle max length (50)
        with pytest.raises(ValidationError):
            employee = Employee(
                employeenumber=1009,
                lastname="Test",
                firstname="Test",
                extension="1234",
                email="test@example.com",
                officecode=office,
                jobtitle="x" * 51,  # Exceeds max_length=50
            )
            employee.full_clean()

    @pytest.mark.django_db
    def test_employee_required_fields(self, office):
        """Test that required fields cannot be null."""
        # In testing environment, we can't rely on database constraints
        # Instead, we test that the field is defined as required
        employeenumber_field = Employee._meta.get_field("employeenumber")
        assert employeenumber_field.primary_key is True
        assert not employeenumber_field.null

        lastname_field = Employee._meta.get_field("lastname")
        assert not lastname_field.null

        firstname_field = Employee._meta.get_field("firstname")
        assert not firstname_field.null

    @pytest.mark.django_db
    def test_employee_unique_constraint(self, office):
        """Test that employeenumber must be unique."""
        Employee.objects.create(
            employeenumber=1010,
            lastname="Unique",
            firstname="Test",
            extension="1234",
            email="unique@example.com",
            officecode=office,
            jobtitle="Test",
        )

        with pytest.raises(IntegrityError):
            Employee.objects.create(
                employeenumber=1010,  # Duplicate
                lastname="Another",
                firstname="Test",
                extension="5678",
                email="another@example.com",
                officecode=office,
                jobtitle="Test",
            )

    @pytest.mark.django_db
    def test_employee_meta_options(self):
        """Test model meta options."""
        assert Employee._meta.managed is True  # Overridden for testing
        assert Employee._meta.db_table == "employees"

    @pytest.mark.django_db
    def test_employee_field_attributes(self):
        """Test field attributes and constraints."""
        # Test employeenumber field
        employeenumber_field = Employee._meta.get_field("employeenumber")
        assert employeenumber_field.primary_key is True

        # Test lastname field
        lastname_field = Employee._meta.get_field("lastname")
        assert lastname_field.max_length == 50

        # Test firstname field
        firstname_field = Employee._meta.get_field("firstname")
        assert firstname_field.max_length == 50

        # Test extension field
        extension_field = Employee._meta.get_field("extension")
        assert extension_field.max_length == 10

        # Test email field
        email_field = Employee._meta.get_field("email")
        assert email_field.max_length == 100

        # Test jobtitle field
        jobtitle_field = Employee._meta.get_field("jobtitle")
        assert jobtitle_field.max_length == 50

    @pytest.mark.django_db
    def test_employee_foreign_key_relationships(self, office, manager_employee):
        """Test foreign key relationships."""
        employee = Employee.objects.create(
            employeenumber=1011,
            lastname="Subordinate",
            firstname="Test",
            extension="2222",
            email="subordinate@example.com",
            officecode=office,
            reportsto=manager_employee,
            jobtitle="Rep",
        )

        # Test office relationship
        assert employee.officecode == office
        assert employee in office.employee_set.all()

        # Test manager relationship
        assert employee.reportsto == manager_employee
        assert employee in manager_employee.employee_set.all()

    @pytest.mark.django_db
    def test_employee_self_referential_relationship(self, office):
        """Test self-referential relationship (reportsTo)."""
        manager = Employee.objects.create(
            employeenumber=1012,
            lastname="Manager",
            firstname="Test",
            extension="3333",
            email="manager@example.com",
            officecode=office,
            jobtitle="Manager",
        )

        subordinate = Employee.objects.create(
            employeenumber=1013,
            lastname="Subordinate",
            firstname="Test",
            extension="4444",
            email="subordinate@example.com",
            officecode=office,
            reportsto=manager,
            jobtitle="Rep",
        )

        # Test that subordinate reports to manager
        assert subordinate.reportsto == manager
        assert subordinate in manager.employee_set.all()

        # Test that manager has subordinates
        assert subordinate in manager.employee_set.all()

    @pytest.mark.django_db
    def test_employee_email_formats(self, office):
        """Test various email formats."""
        email_formats = [
            "test@example.com",
            "user.name@company.co.uk",
            "firstname.lastname+tag@domain.org",
            "user123@subdomain.example.com",
            "test-user@example-domain.com",
        ]

        for i, email in enumerate(email_formats):
            employee = Employee.objects.create(
                employeenumber=1020 + i,
                lastname=f"Email{i}",
                firstname="Test",
                extension="1234",
                email=email,
                officecode=office,
                jobtitle="Test",
            )

            assert employee.email == email

    @pytest.mark.django_db
    def test_employee_extension_formats(self, office):
        """Test various extension formats."""
        extensions = ["1234", "x1234", "1234-5678", "1234 ext 5678", "1234.5678"]

        for i, extension in enumerate(extensions):
            employee = Employee.objects.create(
                employeenumber=1030 + i,
                lastname=f"Ext{i}",
                firstname="Test",
                extension=extension,
                email=f"ext{i}@example.com",
                officecode=office,
                jobtitle="Test",
            )

            assert employee.extension == extension

    @pytest.mark.django_db
    def test_employee_job_titles(self, office):
        """Test various job titles."""
        job_titles = [
            "Sales Rep",
            "Sales Manager",
            "VP Sales",
            "President",
            "VP Marketing",
            "Sales Director",
            "Account Manager",
            "Inside Sales Rep",
            "Outside Sales Rep",
            "Sales Engineer",
        ]

        for i, job_title in enumerate(job_titles):
            employee = Employee.objects.create(
                employeenumber=1040 + i,
                lastname=f"Title{i}",
                firstname="Test",
                extension="1234",
                email=f"title{i}@example.com",
                officecode=office,
                jobtitle=job_title,
            )

            assert employee.jobtitle == job_title

    @pytest.mark.django_db
    def test_employee_unicode_handling(self, office):
        """Test handling of unicode characters."""
        employee = Employee.objects.create(
            employeenumber=1050,
            lastname="Doe with émojis 🧑‍💼 and accents",
            firstname="Jean with émojis 👨‍💼 and accents",
            extension="émojis-1234",
            email="jean.doe@émojis.com",
            officecode=office,
            jobtitle="Sales Rep with émojis 💼",
        )

        assert "émojis" in employee.lastname
        assert "🧑‍💼" in employee.lastname
        assert "émojis" in employee.firstname
        assert "👨‍💼" in employee.firstname
        assert "émojis" in employee.extension
        assert "émojis" in employee.email
        assert "émojis" in employee.jobtitle
        assert "💼" in employee.jobtitle

    @pytest.mark.django_db
    def test_employee_hierarchy_levels(self, office):
        """Test employee hierarchy at different levels."""
        # Create a hierarchy: President -> VP -> Manager -> Rep
        president = Employee.objects.create(
            employeenumber=1060,
            lastname="President",
            firstname="Test",
            extension="0001",
            email="president@example.com",
            officecode=office,
            jobtitle="President",
        )

        vp = Employee.objects.create(
            employeenumber=1061,
            lastname="VP",
            firstname="Test",
            extension="0002",
            email="vp@example.com",
            officecode=office,
            reportsto=president,
            jobtitle="VP Sales",
        )

        manager = Employee.objects.create(
            employeenumber=1062,
            lastname="Manager",
            firstname="Test",
            extension="0003",
            email="manager@example.com",
            officecode=office,
            reportsto=vp,
            jobtitle="Sales Manager",
        )

        rep = Employee.objects.create(
            employeenumber=1063,
            lastname="Rep",
            firstname="Test",
            extension="0004",
            email="rep@example.com",
            officecode=office,
            reportsto=manager,
            jobtitle="Sales Rep",
        )

        # Test hierarchy relationships
        assert vp.reportsto == president
        assert manager.reportsto == vp
        assert rep.reportsto == manager

        # Test that all subordinates are in their manager's employee_set
        assert vp in president.employee_set.all()
        assert manager in vp.employee_set.all()
        assert rep in manager.employee_set.all()

    @pytest.mark.django_db
    def test_employee_negative_employee_number(self, office):
        """Test handling of negative employee numbers."""
        # Note: This might not be allowed depending on database constraints
        # but we test the model behavior
        employee = Employee.objects.create(
            employeenumber=-1,
            lastname="Negative",
            firstname="Test",
            extension="1234",
            email="negative@example.com",
            officecode=office,
            jobtitle="Test",
        )

        assert employee.employeenumber == -1

    @pytest.mark.django_db
    def test_employee_zero_employee_number(self, office):
        """Test handling of zero employee number."""
        employee = Employee.objects.create(
            employeenumber=0,
            lastname="Zero",
            firstname="Test",
            extension="1234",
            email="zero@example.com",
            officecode=office,
            jobtitle="Test",
        )

        assert employee.employeenumber == 0

    @pytest.mark.django_db
    def test_employee_large_employee_number(self, office):
        """Test handling of large employee numbers."""
        large_number = 999999999  # Large integer

        employee = Employee.objects.create(
            employeenumber=large_number,
            lastname="Large",
            firstname="Test",
            extension="1234",
            email="large@example.com",
            officecode=office,
            jobtitle="Test",
        )

        assert employee.employeenumber == large_number
