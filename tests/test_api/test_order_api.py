"""
Tests for Order API endpoints.
"""
import pytest
from datetime import date
from django.urls import reverse
from rest_framework import status

from classicmodels.models import Order, Customer


class TestOrderAPI:
    """Test cases for Order API endpoints."""

    @pytest.mark.django_db
    def test_list_orders_authenticated(self, authenticated_api_client, order):
        """Test listing orders when authenticated."""
        url = reverse('classicmodels:order-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['ordernumber'] == order.ordernumber

    @pytest.mark.django_db
    def test_list_orders_unauthenticated(self, api_client, order):
        """Test listing orders when not authenticated."""
        url = reverse('classicmodels:order-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_order_authenticated(self, authenticated_api_client, order):
        """Test retrieving a specific order when authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['ordernumber'] == order.ordernumber
        assert response.data['status'] == order.status

    @pytest.mark.django_db
    def test_retrieve_order_unauthenticated(self, api_client, order):
        """Test retrieving an order when not authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_order(self, authenticated_api_client):
        """Test retrieving an order that doesn't exist."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': 99999})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_order_authenticated(self, authenticated_api_client, customer):
        """Test creating an order when authenticated."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': 20001,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'shippeddate': '2024-02-18',
            'status': 'Shipped',
            'comments': 'New test order',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['ordernumber'] == 20001
        assert response.data['status'] == 'Shipped'

    @pytest.mark.django_db
    def test_create_order_unauthenticated(self, api_client, customer):
        """Test creating an order when not authenticated."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': 20001,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'customernumber': customer.customernumber
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_order_duplicate_number(self, authenticated_api_client, order, customer):
        """Test creating an order with duplicate order number."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': order.ordernumber,  # Duplicate
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_order_invalid_customer(self, authenticated_api_client):
        """Test creating an order with invalid customer."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': 20002,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'customernumber': 99999  # Invalid customer
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_order_minimal_data(self, authenticated_api_client, customer):
        """Test creating an order with minimal required data."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': 20003,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['ordernumber'] == 20003
        assert response.data['shippeddate'] is None
        assert response.data['comments'] is None

    @pytest.mark.django_db
    def test_update_order_authenticated(self, authenticated_api_client, order):
        """Test updating an order when authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        data = {
            'ordernumber': order.ordernumber,
            'orderdate': '2024-02-16',
            'requireddate': '2024-02-21',
            'shippeddate': '2024-02-19',
            'status': 'Delivered',
            'comments': 'Updated order',
            'customernumber': order.customernumber.customernumber
        }
        
        response = authenticated_api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'Delivered'
        assert response.data['comments'] == 'Updated order'

    @pytest.mark.django_db
    def test_update_order_unauthenticated(self, api_client, order):
        """Test updating an order when not authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        data = {
            'ordernumber': order.ordernumber,
            'orderdate': '2024-02-16',
            'requireddate': '2024-02-21',
            'status': 'Delivered',
            'customernumber': order.customernumber.customernumber
        }
        
        response = api_client.put(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_order_authenticated(self, authenticated_api_client, order):
        """Test partially updating an order when authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        data = {
            'status': 'Cancelled',
            'comments': 'Order cancelled by customer'
        }
        
        response = authenticated_api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'Cancelled'
        assert response.data['comments'] == 'Order cancelled by customer'
        # Other fields should remain unchanged
        assert response.data['ordernumber'] == order.ordernumber

    @pytest.mark.django_db
    def test_partial_update_order_unauthenticated(self, api_client, order):
        """Test partially updating an order when not authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        data = {
            'status': 'Cancelled'
        }
        
        response = api_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_order_authenticated(self, authenticated_api_client, order):
        """Test deleting an order when authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        response = authenticated_api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Order.objects.filter(ordernumber=order.ordernumber).exists()

    @pytest.mark.django_db
    def test_delete_order_unauthenticated(self, api_client, order):
        """Test deleting an order when not authenticated."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_order(self, authenticated_api_client):
        """Test deleting an order that doesn't exist."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': 99999})
        response = authenticated_api_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_order_serializer_validation(self, authenticated_api_client, customer):
        """Test order serializer validation."""
        url = reverse('classicmodels:order-list')
        
        # Test with invalid data (exceeds max length)
        data = {
            'ordernumber': 30001,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'x' * 16,  # Exceeds max_length=15
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_order_status_values(self, authenticated_api_client, customer):
        """Test various order status values."""
        url = reverse('classicmodels:order-list')
        statuses = [
            'In Process',
            'Shipped',
            'Cancelled',
            'On Hold',
            'Disputed',
            'Resolved'
        ]
        
        for i, order_status in enumerate(statuses):
            data = {
                'ordernumber': 30100 + i,
                'orderdate': '2024-02-15',
                'requireddate': '2024-02-20',
                'status': order_status,
                'customernumber': customer.customernumber
            }
            
            response = authenticated_api_client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data['status'] == order_status

    @pytest.mark.django_db
    def test_order_date_relationships(self, authenticated_api_client, customer):
        """Test date field relationships and logic."""
        url = reverse('classicmodels:order-list')
        
        # Test order with shipped date before required date
        data1 = {
            'ordernumber': 30110,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'shippeddate': '2024-02-18',  # Shipped before required
            'status': 'Shipped',
            'customernumber': customer.customernumber
        }
        
        response1 = authenticated_api_client.post(url, data1, format='json')
        assert response1.status_code == status.HTTP_201_CREATED
        assert response1.data['shippeddate'] == '2024-02-18'
        assert response1.data['requireddate'] == '2024-02-20'
        
        # Test order with shipped date after required date
        data2 = {
            'ordernumber': 30111,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'shippeddate': '2024-02-25',  # Shipped after required
            'status': 'Shipped',
            'customernumber': customer.customernumber
        }
        
        response2 = authenticated_api_client.post(url, data2, format='json')
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.data['shippeddate'] == '2024-02-25'
        assert response2.data['requireddate'] == '2024-02-20'

    @pytest.mark.django_db
    def test_order_unicode_handling(self, authenticated_api_client, customer):
        """Test handling of unicode characters in order."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': 30120,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'Process émojis',
            'comments': 'Comments émojis 📦 café',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'émojis' in response.data['status']
        assert 'émojis' in response.data['comments']
        assert '📦' in response.data['comments']
        assert 'café' in response.data['comments']

    @pytest.mark.django_db
    def test_order_large_comments(self, authenticated_api_client, customer):
        """Test handling of large comments."""
        url = reverse('classicmodels:order-list')
        large_comment = 'x' * 10000  # Large text
        
        data = {
            'ordernumber': 30130,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'comments': large_comment,
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data['comments']) == 10000

    @pytest.mark.django_db
    def test_order_negative_order_number(self, authenticated_api_client, customer):
        """Test handling of negative order numbers."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': -1,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['ordernumber'] == -1

    @pytest.mark.django_db
    def test_order_zero_order_number(self, authenticated_api_client, customer):
        """Test handling of zero order number."""
        url = reverse('classicmodels:order-list')
        data = {
            'ordernumber': 0,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['ordernumber'] == 0

    @pytest.mark.django_db
    def test_order_large_order_number(self, authenticated_api_client, customer):
        """Test handling of large order numbers."""
        url = reverse('classicmodels:order-list')
        large_number = 999999999  # Large integer
        
        data = {
            'ordernumber': large_number,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': 'In Process',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['ordernumber'] == large_number

    @pytest.mark.django_db
    def test_order_future_dates(self, authenticated_api_client, customer):
        """Test handling of future dates."""
        url = reverse('classicmodels:order-list')
        future_order_date = '2030-12-31'
        future_required_date = '2031-01-15'
        future_shipped_date = '2031-01-10'
        
        data = {
            'ordernumber': 30140,
            'orderdate': future_order_date,
            'requireddate': future_required_date,
            'shippeddate': future_shipped_date,
            'status': 'In Process',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['orderdate'] == future_order_date
        assert response.data['requireddate'] == future_required_date
        assert response.data['shippeddate'] == future_shipped_date

    @pytest.mark.django_db
    def test_order_past_dates(self, authenticated_api_client, customer):
        """Test handling of past dates."""
        url = reverse('classicmodels:order-list')
        past_order_date = '2020-01-01'
        past_required_date = '2020-01-15'
        past_shipped_date = '2020-01-10'
        
        data = {
            'ordernumber': 30150,
            'orderdate': past_order_date,
            'requireddate': past_required_date,
            'shippeddate': past_shipped_date,
            'status': 'Shipped',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['orderdate'] == past_order_date
        assert response.data['requireddate'] == past_required_date
        assert response.data['shippeddate'] == past_shipped_date

    @pytest.mark.django_db
    def test_order_same_dates(self, authenticated_api_client, customer):
        """Test handling of same dates."""
        url = reverse('classicmodels:order-list')
        same_date = '2024-06-15'
        
        data = {
            'ordernumber': 30160,
            'orderdate': same_date,
            'requireddate': same_date,
            'shippeddate': same_date,
            'status': 'Shipped',
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['orderdate'] == same_date
        assert response.data['requireddate'] == same_date
        assert response.data['shippeddate'] == same_date

    @pytest.mark.django_db
    def test_order_status_length_boundary(self, authenticated_api_client, customer):
        """Test status field at max length boundary."""
        url = reverse('classicmodels:order-list')
        max_status = 'x' * 15  # Exactly max length
        
        data = {
            'ordernumber': 30170,
            'orderdate': '2024-02-15',
            'requireddate': '2024-02-20',
            'status': max_status,
            'customernumber': customer.customernumber
        }
        
        response = authenticated_api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == max_status
        assert len(response.data['status']) == 15

    @pytest.mark.django_db
    def test_order_pagination(self, authenticated_api_client, customer):
        """Test order pagination."""
        # Create additional orders beyond the existing ones
        for i in range(15):  # More than default page size
            Order.objects.create(
                ordernumber=40000 + i,
                orderdate='2024-02-15',
                requireddate='2024-02-20',
                status='In Process',
                customernumber=customer
            )
        
        url = reverse('classicmodels:order-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    @pytest.mark.django_db
    def test_order_ordering(self, authenticated_api_client, customer):
        """Test order ordering."""
        # Create orders in specific order
        Order.objects.create(
            ordernumber=50001,
            orderdate='2024-02-15',
            requireddate='2024-02-20',
            status='In Process',
            customernumber=customer
        )
        Order.objects.create(
            ordernumber=50002,
            orderdate='2024-02-16',
            requireddate='2024-02-21',
            status='Shipped',
            customernumber=customer
        )
        
        url = reverse('classicmodels:order-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data['results']) >= 2

    @pytest.mark.django_db
    def test_order_relationships(self, authenticated_api_client, order, customer):
        """Test order relationships in API response."""
        url = reverse('classicmodels:order-detail', kwargs={'ordernumber': order.ordernumber})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'customernumber' in response.data
        assert response.data['customernumber'] == customer.customernumber
