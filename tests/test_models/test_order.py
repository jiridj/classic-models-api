"""
Tests for Order model.
"""
import pytest
from datetime import date
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from classicmodels.models import Order, Customer


class TestOrderModel:
    """Test cases for Order model."""

    @pytest.mark.django_db
    def test_order_creation(self, customer):
        """Test creating an order with all fields."""
        order = Order.objects.create(
            ordernumber=10001,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            shippeddate=date(2024, 1, 18),
            status='Shipped',
            comments='Test order with comments',
            customernumber=customer
        )
        
        assert order.ordernumber == 10001
        assert order.orderdate == date(2024, 1, 15)
        assert order.requireddate == date(2024, 1, 20)
        assert order.shippeddate == date(2024, 1, 18)
        assert order.status == 'Shipped'
        assert order.comments == 'Test order with comments'
        assert order.customernumber == customer

    @pytest.mark.django_db
    def test_order_creation_minimal(self, customer):
        """Test creating an order with only required fields."""
        order = Order.objects.create(
            ordernumber=10002,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        assert order.ordernumber == 10002
        assert order.orderdate == date(2024, 1, 15)
        assert order.requireddate == date(2024, 1, 20)
        assert order.status == 'In Process'
        assert order.customernumber == customer
        assert order.shippeddate is None
        assert order.comments is None

    @pytest.mark.django_db
    def test_order_string_representation(self, customer):
        """Test the string representation of Order."""
        order = Order.objects.create(
            ordernumber=10003,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        assert str(order) == '10003'

    @pytest.mark.django_db
    def test_order_primary_key(self, customer):
        """Test that ordernumber is the primary key."""
        order = Order.objects.create(
            ordernumber=10004,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        assert order.pk == 10004

    @pytest.mark.django_db
    def test_order_max_length_constraints(self, customer):
        """Test field max length constraints."""
        # Test status max length (15)
        with pytest.raises(ValidationError):
            order = Order(
                ordernumber=10005,
                orderdate=date(2024, 1, 15),
                requireddate=date(2024, 1, 20),
                status='x' * 16,  # Exceeds max_length=15
                customernumber=customer
            )
            order.full_clean()

    @pytest.mark.django_db
    def test_order_blank_fields(self, customer):
        """Test that optional fields can be blank."""
        order = Order.objects.create(
            ordernumber=10006,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            comments='',  # Empty string should be allowed
            customernumber=customer
        )
        
        assert order.comments == ''

    @pytest.mark.django_db
    def test_order_null_fields(self, customer):
        """Test that optional fields can be null."""
        order = Order.objects.create(
            ordernumber=10007,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            shippeddate=None,
            comments=None,
            customernumber=customer
        )
        
        assert order.shippeddate is None
        assert order.comments is None

    @pytest.mark.django_db
    def test_order_unique_constraint(self, customer):
        """Test that ordernumber must be unique."""
        Order.objects.create(
            ordernumber=10008,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        with pytest.raises(IntegrityError):
            Order.objects.create(
                ordernumber=10008,  # Duplicate
                orderdate=date(2024, 1, 16),
                requireddate=date(2024, 1, 21),
                status='Shipped',
                customernumber=customer
            )

    @pytest.mark.django_db
    def test_order_meta_options(self):
        """Test model meta options."""
        assert Order._meta.managed is True  # Overridden for testing
        assert Order._meta.db_table == 'orders'

    @pytest.mark.django_db
    def test_order_field_attributes(self):
        """Test field attributes and constraints."""
        # Test ordernumber field
        ordernumber_field = Order._meta.get_field('ordernumber')
        assert ordernumber_field.primary_key is True
        
        # Test status field
        status_field = Order._meta.get_field('status')
        assert status_field.max_length == 15
        
        # Test comments field
        comments_field = Order._meta.get_field('comments')
        assert comments_field.blank is True
        assert comments_field.null is True
        
        # Test shippeddate field
        shippeddate_field = Order._meta.get_field('shippeddate')
        assert shippeddate_field.blank is True
        assert shippeddate_field.null is True

    @pytest.mark.django_db
    def test_order_foreign_key_relationships(self, customer):
        """Test foreign key relationships."""
        order = Order.objects.create(
            ordernumber=10009,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        # Test customer relationship
        assert order.customernumber == customer
        assert order in customer.order_set.all()

    @pytest.mark.django_db
    def test_order_status_values(self, customer):
        """Test various order status values."""
        statuses = [
            'In Process',
            'Shipped',
            'Cancelled',
            'On Hold',
            'Disputed',
            'Resolved'
        ]
        
        for i, status in enumerate(statuses):
            order = Order.objects.create(
                ordernumber=10100 + i,
                orderdate=date(2024, 1, 15),
                requireddate=date(2024, 1, 20),
                status=status,
                customernumber=customer
            )
            
            assert order.status == status

    @pytest.mark.django_db
    def test_order_date_relationships(self, customer):
        """Test date field relationships and logic."""
        # Test order with shipped date before required date
        order1 = Order.objects.create(
            ordernumber=10110,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            shippeddate=date(2024, 1, 18),  # Shipped before required
            status='Shipped',
            customernumber=customer
        )
        
        assert order1.shippeddate < order1.requireddate
        
        # Test order with shipped date after required date
        order2 = Order.objects.create(
            ordernumber=10111,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            shippeddate=date(2024, 1, 25),  # Shipped after required
            status='Shipped',
            customernumber=customer
        )
        
        assert order2.shippeddate > order2.requireddate

    @pytest.mark.django_db
    def test_order_unicode_handling(self, customer):
        """Test handling of unicode characters."""
        order = Order.objects.create(
            ordernumber=10120,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process with émojis 🚚',
            comments='Comments with émojis 📦 and accents café',
            customernumber=customer
        )
        
        assert 'émojis' in order.status
        assert '🚚' in order.status
        assert 'émojis' in order.comments
        assert '📦' in order.comments
        assert 'café' in order.comments

    @pytest.mark.django_db
    def test_order_large_comments(self, customer):
        """Test handling of large comments."""
        large_comment = 'x' * 10000  # Large text
        
        order = Order.objects.create(
            ordernumber=10130,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            comments=large_comment,
            customernumber=customer
        )
        
        assert len(order.comments) == 10000

    @pytest.mark.django_db
    def test_order_negative_order_number(self, customer):
        """Test handling of negative order numbers."""
        order = Order.objects.create(
            ordernumber=-1,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        assert order.ordernumber == -1

    @pytest.mark.django_db
    def test_order_zero_order_number(self, customer):
        """Test handling of zero order number."""
        order = Order.objects.create(
            ordernumber=0,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        assert order.ordernumber == 0

    @pytest.mark.django_db
    def test_order_large_order_number(self, customer):
        """Test handling of large order numbers."""
        large_number = 999999999  # Large integer
        
        order = Order.objects.create(
            ordernumber=large_number,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        assert order.ordernumber == large_number

    @pytest.mark.django_db
    def test_order_future_dates(self, customer):
        """Test handling of future dates."""
        future_order_date = date(2030, 12, 31)
        future_required_date = date(2031, 1, 15)
        future_shipped_date = date(2031, 1, 10)
        
        order = Order.objects.create(
            ordernumber=10140,
            orderdate=future_order_date,
            requireddate=future_required_date,
            shippeddate=future_shipped_date,
            status='In Process',
            customernumber=customer
        )
        
        assert order.orderdate == future_order_date
        assert order.requireddate == future_required_date
        assert order.shippeddate == future_shipped_date

    @pytest.mark.django_db
    def test_order_past_dates(self, customer):
        """Test handling of past dates."""
        past_order_date = date(2020, 1, 1)
        past_required_date = date(2020, 1, 15)
        past_shipped_date = date(2020, 1, 10)
        
        order = Order.objects.create(
            ordernumber=10150,
            orderdate=past_order_date,
            requireddate=past_required_date,
            shippeddate=past_shipped_date,
            status='Shipped',
            customernumber=customer
        )
        
        assert order.orderdate == past_order_date
        assert order.requireddate == past_required_date
        assert order.shippeddate == past_shipped_date

    @pytest.mark.django_db
    def test_order_same_dates(self, customer):
        """Test handling of same dates."""
        same_date = date(2024, 6, 15)
        
        order = Order.objects.create(
            ordernumber=10160,
            orderdate=same_date,
            requireddate=same_date,
            shippeddate=same_date,
            status='Shipped',
            customernumber=customer
        )
        
        assert order.orderdate == same_date
        assert order.requireddate == same_date
        assert order.shippeddate == same_date

    @pytest.mark.django_db
    def test_order_status_length_boundary(self, customer):
        """Test status field at max length boundary."""
        max_status = 'x' * 15  # Exactly max length
        
        order = Order.objects.create(
            ordernumber=10170,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status=max_status,
            customernumber=customer
        )
        
        assert order.status == max_status
        assert len(order.status) == 15

    @pytest.mark.django_db
    def test_order_multiple_customers(self, customer, employee):
        """Test orders for multiple customers."""
        # Create another customer
        customer2 = Customer.objects.create(
            customernumber=2001,
            customername='Second Customer',
            contactlastname='Second',
            contactfirstname='Test',
            phone='+1-555-0000',
            addressline1='123 Second Ave',
            city='Second City',
            country='USA',
            salesrepemployeenumber=employee
        )
        
        # Create orders for both customers
        order1 = Order.objects.create(
            ordernumber=10180,
            orderdate=date(2024, 1, 15),
            requireddate=date(2024, 1, 20),
            status='In Process',
            customernumber=customer
        )
        
        order2 = Order.objects.create(
            ordernumber=10181,
            orderdate=date(2024, 1, 16),
            requireddate=date(2024, 1, 21),
            status='Shipped',
            customernumber=customer2
        )
        
        # Test relationships
        assert order1.customernumber == customer
        assert order2.customernumber == customer2
        assert order1 in customer.order_set.all()
        assert order2 in customer2.order_set.all()
        assert order1 not in customer2.order_set.all()
        assert order2 not in customer.order_set.all()
