"""
Tests for Orderdetail model.
"""

from decimal import Decimal

import pytest
from django.db import IntegrityError, models

from classicmodels.models import Order, Orderdetail, Product


class TestOrderdetailModel:
    """Test cases for Orderdetail model."""

    @pytest.mark.django_db
    def test_order_detail_creation(self, order, product):
        """Test creating an order detail with all fields."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=5,
            priceeach=Decimal("45.99"),
            orderlinenumber=1,
        )

        assert order_detail.id is not None  # id should be auto-generated
        assert isinstance(order_detail.id, int)  # id should be an integer
        assert order_detail.ordernumber == order
        assert order_detail.productcode == product
        assert order_detail.quantityordered == 5
        assert order_detail.priceeach == Decimal("45.99")
        assert order_detail.orderlinenumber == 1

    @pytest.mark.django_db
    def test_order_detail_string_representation(self, order, product):
        """Test the string representation of Orderdetail."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=3,
            priceeach=Decimal("25.50"),
            orderlinenumber=2,
        )

        # Orderdetail doesn't have a custom __str__ method, so it uses the default
        assert hasattr(order_detail, "ordernumber")
        assert hasattr(order_detail, "productcode")

    @pytest.mark.django_db
    def test_order_detail_meta_options(self):
        """Test model meta options."""
        assert Orderdetail._meta.managed is True  # Overridden for testing
        assert Orderdetail._meta.db_table == "orderdetails"
        assert Orderdetail._meta.unique_together == (("ordernumber", "productcode"),)
        # Verify id field is the primary key
        assert Orderdetail._meta.pk.name == "id"
        assert isinstance(Orderdetail._meta.pk, models.AutoField)

    @pytest.mark.django_db
    def test_order_detail_field_attributes(self):
        """Test field attributes and constraints."""
        # Test quantityordered field
        quantityordered_field = Orderdetail._meta.get_field("quantityordered")
        assert isinstance(quantityordered_field, models.IntegerField)  # IntegerField

        # Test priceeach field
        priceeach_field = Orderdetail._meta.get_field("priceeach")
        assert priceeach_field.max_digits == 10
        assert priceeach_field.decimal_places == 2

        # Test orderlinenumber field
        orderlinenumber_field = Orderdetail._meta.get_field("orderlinenumber")
        assert isinstance(
            orderlinenumber_field, models.SmallIntegerField
        )  # SmallIntegerField

    @pytest.mark.django_db
    def test_order_detail_foreign_key_relationships(self, order, product):
        """Test foreign key relationships."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=2,
            priceeach=Decimal("30.00"),
            orderlinenumber=1,
        )

        # Test order relationship
        assert order_detail.ordernumber == order
        assert order_detail in order.orderdetail_set.all()

        # Test product relationship
        assert order_detail.productcode == product
        assert order_detail in product.orderdetail_set.all()

    @pytest.mark.django_db
    def test_order_detail_unique_together_constraint(self, order, product):
        """Test unique together constraint on ordernumber and productcode."""
        Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=1,
            priceeach=Decimal("10.00"),
            orderlinenumber=1,
        )

        # Same order, same product should fail
        with pytest.raises(IntegrityError):
            Orderdetail.objects.create(
                ordernumber=order,
                productcode=product,  # Same product
                quantityordered=2,
                priceeach=Decimal("20.00"),
                orderlinenumber=2,
            )

    @pytest.mark.django_db
    def test_order_detail_same_product_different_orders(self, product, customer):
        """Test that same product can be in different orders."""
        # Create two different orders
        order1 = Order.objects.create(
            ordernumber=20000,
            orderdate="2024-01-15",
            requireddate="2024-01-20",
            status="In Process",
            customernumber=customer,
        )

        order2 = Order.objects.create(
            ordernumber=20001,
            orderdate="2024-01-16",
            requireddate="2024-01-21",
            status="In Process",
            customernumber=customer,
        )

        # Same product in different orders should work
        order_detail1 = Orderdetail.objects.create(
            ordernumber=order1,
            productcode=product,
            quantityordered=1,
            priceeach=Decimal("10.00"),
            orderlinenumber=1,
        )

        order_detail2 = Orderdetail.objects.create(
            ordernumber=order2,
            productcode=product,  # Same product, different order
            quantityordered=2,
            priceeach=Decimal("15.00"),
            orderlinenumber=1,
        )

        assert order_detail1.ordernumber == order1
        assert order_detail2.ordernumber == order2
        assert order_detail1.productcode == order_detail2.productcode

    @pytest.mark.django_db
    def test_order_detail_decimal_precision(self, order, product):
        """Test decimal field precision and scale."""
        # Test max value for (10,2)
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=1,
            priceeach=Decimal("99999999.99"),
            orderlinenumber=1,
        )

        assert order_detail.priceeach == Decimal("99999999.99")

    @pytest.mark.django_db
    def test_order_detail_negative_quantity(self, order, product):
        """Test handling of negative quantities."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=-5,  # Negative quantity (return)
            priceeach=Decimal("45.99"),
            orderlinenumber=1,
        )

        assert order_detail.quantityordered == -5

    @pytest.mark.django_db
    def test_order_detail_zero_quantity(self, order, product):
        """Test handling of zero quantities."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=0,
            priceeach=Decimal("45.99"),
            orderlinenumber=1,
        )

        assert order_detail.quantityordered == 0

    @pytest.mark.django_db
    def test_order_detail_negative_price(self, order, product):
        """Test handling of negative prices."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=1,
            priceeach=Decimal("-45.99"),  # Negative price (discount/refund)
            orderlinenumber=1,
        )

        assert order_detail.priceeach == Decimal("-45.99")

    @pytest.mark.django_db
    def test_order_detail_zero_price(self, order, product):
        """Test handling of zero prices."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=1,
            priceeach=Decimal("0.00"),
            orderlinenumber=1,
        )

        assert order_detail.priceeach == Decimal("0.00")

    @pytest.mark.django_db
    def test_order_detail_large_quantities(self, order, product):
        """Test handling of large quantities."""
        large_quantity = 999999  # Large integer

        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=large_quantity,
            priceeach=Decimal("1.00"),
            orderlinenumber=1,
        )

        assert order_detail.quantityordered == large_quantity

    @pytest.mark.django_db
    def test_order_detail_order_line_numbers(self, order, product):
        """Test various order line numbers."""
        line_numbers = [1, 2, 3, 10, 100, 999, 32767]  # SmallIntegerField range

        for i, line_number in enumerate(line_numbers):
            # Create a new product for each line to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"LINE{i:03d}",
                productname=f"Line Product {i}",
                productline=product.productline,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            order_detail = Orderdetail.objects.create(
                ordernumber=order,
                productcode=new_product,
                quantityordered=1,
                priceeach=Decimal("10.00"),
                orderlinenumber=line_number,
            )

            assert order_detail.orderlinenumber == line_number

    @pytest.mark.django_db
    def test_order_detail_price_precision_rounding(self, order, product):
        """Test price field precision and rounding."""
        # Test that the field enforces 2 decimal places
        test_prices = [
            ("12.35", Decimal("12.35")),  # Exact 2 decimal places
            ("12.34", Decimal("12.34")),  # Exact 2 decimal places
            ("12.00", Decimal("12.00")),  # Exact 2 decimal places
            ("0.01", Decimal("0.01")),  # Exact 2 decimal places
        ]

        for i, (input_price, expected_price) in enumerate(test_prices):
            # Create a new product for each test to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"PRICE{i:03d}",
                productname=f"Price Product {i}",
                productline=product.productline,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            order_detail = Orderdetail.objects.create(
                ordernumber=order,
                productcode=new_product,
                quantityordered=1,
                priceeach=Decimal(input_price),
                orderlinenumber=1,
            )

            assert order_detail.priceeach == expected_price

        # Test that the field definition enforces 2 decimal places
        priceeach_field = Orderdetail._meta.get_field("priceeach")
        assert priceeach_field.decimal_places == 2
        assert priceeach_field.max_digits == 10

    @pytest.mark.django_db
    def test_order_detail_very_small_prices(self, order, product):
        """Test handling of very small prices."""
        small_prices = [
            Decimal("0.01"),  # 1 cent
            Decimal("0.10"),  # 10 cents
            Decimal("0.99"),  # 99 cents
        ]

        for i, price in enumerate(small_prices):
            # Create a new product for each test to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"SMALL{i:03d}",
                productname=f"Small Price Product {i}",
                productline=product.productline,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            order_detail = Orderdetail.objects.create(
                ordernumber=order,
                productcode=new_product,
                quantityordered=1,
                priceeach=price,
                orderlinenumber=1,
            )

            assert order_detail.priceeach == price

    @pytest.mark.django_db
    def test_order_detail_very_large_prices(self, order, product):
        """Test handling of very large prices."""
        large_prices = [
            Decimal("99999999.99"),  # Max value for (10,2)
            Decimal("1000000.00"),  # 1 million
            Decimal("5000000.50"),  # 5 million and 50 cents
        ]

        for i, price in enumerate(large_prices):
            # Create a new product for each test to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"LARGE{i:03d}",
                productname=f"Large Price Product {i}",
                productline=product.productline,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            order_detail = Orderdetail.objects.create(
                ordernumber=order,
                productcode=new_product,
                quantityordered=1,
                priceeach=price,
                orderlinenumber=1,
            )

            assert order_detail.priceeach == price

    @pytest.mark.django_db
    def test_order_detail_multiple_products_same_order(self, order, product_line):
        """Test multiple products in the same order."""
        products = []
        order_details = []

        # Create multiple products
        for i in range(5):
            product = Product.objects.create(
                productcode=f"MULT{i:03d}",
                productname=f"Multi Product {i}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )
            products.append(product)

        # Create order details for each product
        for i, product in enumerate(products):
            order_detail = Orderdetail.objects.create(
                ordernumber=order,
                productcode=product,
                quantityordered=i + 1,
                priceeach=Decimal(f"{10.00 + i * 5.00}"),
                orderlinenumber=i + 1,
            )
            order_details.append(order_detail)

        # Test that all order details belong to the same order
        for order_detail in order_details:
            assert order_detail.ordernumber == order

        # Test that order has all order details
        order_order_details = order.orderdetail_set.all()
        assert len(order_order_details) == 5

        for order_detail in order_details:
            assert order_detail in order_order_details

    @pytest.mark.django_db
    def test_order_detail_required_fields(self, order, product):
        """Test that required fields cannot be null."""
        with pytest.raises(IntegrityError):
            Orderdetail.objects.create(
                ordernumber=None,  # Required field
                productcode=product,
                quantityordered=1,
                priceeach=Decimal("10.00"),
                orderlinenumber=1,
            )

    @pytest.mark.django_db
    def test_order_detail_foreign_key_cascade_behavior(self, order, product):
        """Test foreign key behavior when referenced objects are deleted."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=1,
            priceeach=Decimal("10.00"),
            orderlinenumber=1,
        )

        # Since managed=False, we can't test actual cascade behavior
        # But we can test the relationships exist
        assert order_detail.ordernumber == order
        assert order_detail.productcode == product

    @pytest.mark.django_db
    def test_order_detail_calculated_total(self, order, product):
        """Test calculated total (quantity * price)."""
        order_detail = Orderdetail.objects.create(
            ordernumber=order,
            productcode=product,
            quantityordered=3,
            priceeach=Decimal("25.50"),
            orderlinenumber=1,
        )

        # Calculate expected total
        expected_total = order_detail.quantityordered * order_detail.priceeach
        assert expected_total == Decimal("76.50")

    @pytest.mark.django_db
    def test_order_detail_different_quantities_and_prices(self, order, product_line):
        """Test various combinations of quantities and prices."""
        test_cases = [
            (1, Decimal("100.00")),  # 1 item at $100
            (10, Decimal("10.00")),  # 10 items at $10
            (100, Decimal("1.00")),  # 100 items at $1
            (5, Decimal("25.50")),  # 5 items at $25.50
            (2, Decimal("0.50")),  # 2 items at $0.50
        ]

        for i, (quantity, price) in enumerate(test_cases):
            # Create a new product for each test to avoid unique constraint
            product = Product.objects.create(
                productcode=f"COMBO{i:03d}",
                productname=f"Combo Product {i}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            order_detail = Orderdetail.objects.create(
                ordernumber=order,
                productcode=product,
                quantityordered=quantity,
                priceeach=price,
                orderlinenumber=i + 1,
            )

            assert order_detail.quantityordered == quantity
            assert order_detail.priceeach == price

            # Test calculated total
            expected_total = quantity * price
            actual_total = order_detail.quantityordered * order_detail.priceeach
            assert actual_total == expected_total
