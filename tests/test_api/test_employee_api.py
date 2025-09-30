"""
Tests for Employee API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status

from classicmodels.models import Employee, Office


class TestEmployeeAPI:
    """Test cases for Employee API endpoints."""

    @pytest.mark.django_db
    def test_list_employees_authenticated(self, authenticated_api_client, employee):
        """Test listing employees when authenticated."""
        url = reverse('classicmodels:employee-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['employeenumber'] == employee.employeenumber

    @pytest.mark.django_db
    def test_list_employees_unauthenticated(self, api_client, employee):
        """Test listing employees when not authenticated."""
        url = reverse('classicmodels:employee-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_employee_authenticated(self, authenticated_api_client, employee):
        """Test retrieving a specific employee when authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['employeenumber'] == employee.employeenumber
        assert response.data['lastname'] == employee.lastname

    @pytest.mark.django_db
    def test_retrieve_employee_unauthenticated(self, api_client, employee):
        """Test retrieving an employee when not authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_employee(self, authenticated_api_client):
        """Test retrieving an employee that doesn't exist."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': 99999})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_employee_authenticated(self, authenticated_api_client, office):
        """Test creating an employee when authenticated."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': 2001,
            'lastname': 'New Employee',
            'firstname': 'John',
            'extension': '9999',
            'email': 'john.new@example.com',
            'officecode': office.officecode,
            'jobtitle': 'New Position'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['employeenumber'] == 2001
        assert response.data['lastname'] == 'New Employee'

    @pytest.mark.django_db
    def test_create_employee_unauthenticated(self, api_client, office):
        """Test creating an employee when not authenticated."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': 2001,
            'lastname': 'New Employee',
            'firstname': 'John',
            'extension': '9999',
            'email': 'john.new@example.com',
            'officecode': office.officecode,
            'jobtitle': 'New Position'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_employee_duplicate_number(self, authenticated_api_client, employee, office):
        """Test creating an employee with duplicate employee number."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': employee.employeenumber,  # Duplicate
            'lastname': 'Duplicate Employee',
            'firstname': 'Jane',
            'extension': '8888',
            'email': 'jane.duplicate@example.com',
            'officecode': office.officecode,
            'jobtitle': 'Duplicate Position'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_employee_with_manager(self, authenticated_api_client, office, manager_employee):
        """Test creating an employee with a manager."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': 2002,
            'lastname': 'Subordinate',
            'firstname': 'Bob',
            'extension': '7777',
            'email': 'bob.subordinate@example.com',
            'officecode': office.officecode,
            'reportsto': manager_employee.employeenumber,
            'jobtitle': 'Subordinate Position'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reportsto'] == manager_employee.employeenumber

    @pytest.mark.django_db
    def test_create_employee_invalid_office(self, authenticated_api_client):
        """Test creating an employee with invalid office."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': 2003,
            'lastname': 'Invalid Office',
            'firstname': 'Test',
            'extension': '6666',
            'email': 'test.invalid@example.com',
            'officecode': 'NONEXISTENT',  # Invalid office
            'jobtitle': 'Test Position'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_employee_minimal_data(self, authenticated_api_client, office):
        """Test creating an employee with minimal required data."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': 2004,
            'lastname': 'Minimal',
            'firstname': 'Employee',
            'extension': '5555',
            'email': 'minimal@example.com',
            'officecode': office.officecode,
            'jobtitle': 'Minimal Position'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['employeenumber'] == 2004
        assert response.data['reportsto'] is None

    @pytest.mark.django_db
    def test_update_employee_authenticated(self, authenticated_api_client, employee):
        """Test updating an employee when authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        data = {
            'employeenumber': employee.employeenumber,
            'lastname': 'Updated Employee',
            'firstname': 'Updated',
            'extension': '4444',
            'email': 'updated@example.com',
            'officecode': employee.officecode.officecode,
            'jobtitle': 'Updated Position'
        }
        
        response = authenticated_api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['lastname'] == 'Updated Employee'
        assert response.data['email'] == 'updated@example.com'

    @pytest.mark.django_db
    def test_update_employee_unauthenticated(self, api_client, employee):
        """Test updating an employee when not authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        data = {
            'employeenumber': employee.employeenumber,
            'lastname': 'Updated Employee',
            'firstname': 'Updated',
            'extension': '4444',
            'email': 'updated@example.com',
            'officecode': employee.officecode.officecode,
            'jobtitle': 'Updated Position'
        }
        
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_employee_authenticated(self, authenticated_api_client, employee):
        """Test partially updating an employee when authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        data = {
            'lastname': 'Partially Updated',
            'email': 'partially.updated@example.com'
        }
        
        response = authenticated_api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['lastname'] == 'Partially Updated'
        assert response.data['email'] == 'partially.updated@example.com'
        # Other fields should remain unchanged
        assert response.data['employeenumber'] == employee.employeenumber

    @pytest.mark.django_db
    def test_partial_update_employee_unauthenticated(self, api_client, employee):
        """Test partially updating an employee when not authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        data = {
            'lastname': 'Partially Updated'
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_employee_authenticated(self, authenticated_api_client, employee):
        """Test deleting an employee when authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        response = authenticated_api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Employee.objects.filter(employeenumber=employee.employeenumber).exists()

    @pytest.mark.django_db
    def test_delete_employee_unauthenticated(self, api_client, employee):
        """Test deleting an employee when not authenticated."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_employee(self, authenticated_api_client):
        """Test deleting an employee that doesn't exist."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': 99999})
        response = authenticated_api_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_employee_serializer_validation(self, authenticated_api_client, office):
        """Test employee serializer validation."""
        url = reverse('classicmodels:employee-list')
        
        # Test with invalid data (exceeds max length)
        data = {
            'employeenumber': 3001,
            'lastname': 'x' * 51,  # Exceeds max_length=50
            'firstname': 'Valid',
            'extension': '1234',
            'email': 'valid@example.com',
            'officecode': office.officecode,
            'jobtitle': 'Valid Position'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_employee_email_formats(self, authenticated_api_client, office):
        """Test various email formats."""
        url = reverse('classicmodels:employee-list')
        email_formats = [
            'test@example.com',
            'user.name@company.co.uk',
            'firstname.lastname+tag@domain.org',
            'user123@subdomain.example.com',
            'test-user@example-domain.com'
        ]
        
        for i, email in enumerate(email_formats):
            data = {
                'employeenumber': 3010 + i,
                'lastname': f'Email{i}',
                'firstname': 'Test',
                'extension': '1234',
                'email': email,
                'officecode': office.officecode,
                'jobtitle': 'Test'
            }
            
            response = authenticated_api_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['email'] == email

    @pytest.mark.django_db
    def test_employee_extension_formats(self, authenticated_api_client, office):
        """Test various extension formats."""
        url = reverse('classicmodels:employee-list')
        extensions = ['1234', 'x1234', '1234-5678', '1234.5678', '1234x5678']
        
        for i, extension in enumerate(extensions):
            data = {
                'employeenumber': 3020 + i,
                'lastname': f'Ext{i}',
                'firstname': 'Test',
                'extension': extension,
                'email': f'ext{i}@example.com',
                'officecode': office.officecode,
                'jobtitle': 'Test'
            }
            
            response = authenticated_api_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['extension'] == extension

    @pytest.mark.django_db
    def test_employee_job_titles(self, authenticated_api_client, office):
        """Test various job titles."""
        url = reverse('classicmodels:employee-list')
        job_titles = [
            'Sales Rep',
            'Sales Manager',
            'VP Sales',
            'President',
            'VP Marketing',
            'Sales Director',
            'Account Manager',
            'Inside Sales Rep',
            'Outside Sales Rep',
            'Sales Engineer'
        ]
        
        for i, job_title in enumerate(job_titles):
            data = {
                'employeenumber': 3030 + i,
                'lastname': f'Title{i}',
                'firstname': 'Test',
                'extension': '1234',
                'email': f'title{i}@example.com',
                'officecode': office.officecode,
                'jobtitle': job_title
            }
            
            response = authenticated_api_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['jobtitle'] == job_title

    @pytest.mark.django_db
    def test_employee_unicode_handling(self, authenticated_api_client, office):
        """Test handling of unicode characters in employee."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': 3040,
            'lastname': 'Doe émojis 🧑‍💼',
            'firstname': 'Jean émojis 👨‍💼',
            'extension': 'émojis-1',
            'email': 'jean.doe@émojis.com',
            'officecode': office.officecode,
            'jobtitle': 'Sales Rep émojis 💼'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'émojis' in response.data['lastname']
        assert '🧑‍💼' in response.data['lastname']
        assert 'émojis' in response.data['firstname']
        assert '👨‍💼' in response.data['firstname']
        assert 'émojis' in response.data['extension']
        assert 'émojis' in response.data['email']
        assert 'émojis' in response.data['jobtitle']
        assert '💼' in response.data['jobtitle']

    @pytest.mark.django_db
    def test_employee_hierarchy_levels(self, authenticated_api_client, office):
        """Test employee hierarchy at different levels."""
        url = reverse('classicmodels:employee-list')
        
        # Create a hierarchy: President -> VP -> Manager -> Rep
        president_data = {
            'employeenumber': 3050,
            'lastname': 'President',
            'firstname': 'Test',
            'extension': '0001',
            'email': 'president@example.com',
            'officecode': office.officecode,
            'jobtitle': 'President'
        }
        
        response = authenticated_api_client.post(url, president_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        
        vp_data = {
            'employeenumber': 3051,
            'lastname': 'VP',
            'firstname': 'Test',
            'extension': '0002',
            'email': 'vp@example.com',
            'officecode': office.officecode,
            'reportsto': 3050,
            'jobtitle': 'VP Sales'
        }
        
        response = authenticated_api_client.post(url, vp_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reportsto'] == 3050
        
        manager_data = {
            'employeenumber': 3052,
            'lastname': 'Manager',
            'firstname': 'Test',
            'extension': '0003',
            'email': 'manager@example.com',
            'officecode': office.officecode,
            'reportsto': 3051,
            'jobtitle': 'Sales Manager'
        }
        
        response = authenticated_api_client.post(url, manager_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reportsto'] == 3051
        
        rep_data = {
            'employeenumber': 3053,
            'lastname': 'Rep',
            'firstname': 'Test',
            'extension': '0004',
            'email': 'rep@example.com',
            'officecode': office.officecode,
            'reportsto': 3052,
            'jobtitle': 'Sales Rep'
        }
        
        response = authenticated_api_client.post(url, rep_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reportsto'] == 3052

    @pytest.mark.django_db
    def test_employee_negative_employee_number(self, authenticated_api_client, office):
        """Test handling of negative employee numbers."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': -1,
            'lastname': 'Negative',
            'firstname': 'Test',
            'extension': '1234',
            'email': 'negative@example.com',
            'officecode': office.officecode,
            'jobtitle': 'Test'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['employeenumber'] == -1

    @pytest.mark.django_db
    def test_employee_zero_employee_number(self, authenticated_api_client, office):
        """Test handling of zero employee number."""
        url = reverse('classicmodels:employee-list')
        data = {
            'employeenumber': 0,
            'lastname': 'Zero',
            'firstname': 'Test',
            'extension': '1234',
            'email': 'zero@example.com',
            'officecode': office.officecode,
            'jobtitle': 'Test'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['employeenumber'] == 0

    @pytest.mark.django_db
    def test_employee_large_employee_number(self, authenticated_api_client, office):
        """Test handling of large employee numbers."""
        url = reverse('classicmodels:employee-list')
        large_number = 999999999  # Large integer
        
        data = {
            'employeenumber': large_number,
            'lastname': 'Large',
            'firstname': 'Test',
            'extension': '1234',
            'email': 'large@example.com',
            'officecode': office.officecode,
            'jobtitle': 'Test'
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['employeenumber'] == large_number

    @pytest.mark.django_db
    def test_employee_pagination(self, authenticated_api_client, office):
        """Test employee pagination."""
        # Create additional employees beyond the existing ones
        for i in range(15):  # More than default page size
            Employee.objects.create(
                employeenumber=4000 + i,
                lastname=f'Pagination Employee {i}',
                firstname='Test',
                extension=f'{1000+i:04d}',
                email=f'pagination{i}@example.com',
                officecode=office,
                jobtitle='Test Position'
            )
        
        url = reverse('classicmodels:employee-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    @pytest.mark.django_db
    def test_employee_ordering(self, authenticated_api_client, office):
        """Test employee ordering."""
        # Create employees in specific order
        Employee.objects.create(
            employeenumber=5001,
            lastname='Z Employee',
            firstname='Test',
            extension='0001',
            email='z@example.com',
            officecode=office,
            jobtitle='Test'
        )
        Employee.objects.create(
            employeenumber=5002,
            lastname='A Employee',
            firstname='Test',
            extension='0002',
            email='a@example.com',
            officecode=office,
            jobtitle='Test'
        )
        
        url = reverse('classicmodels:employee-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data['results']) >= 2

    @pytest.mark.django_db
    def test_employee_relationships(self, authenticated_api_client, employee, office):
        """Test employee relationships in API response."""
        url = reverse('classicmodels:employee-detail', kwargs={'employeenumber': employee.employeenumber})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'officecode' in response.data
        assert response.data['officecode'] == office.officecode
