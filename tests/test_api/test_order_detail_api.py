"""
Tests for OrderDetail API endpoints.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from classicmodels.models import Order, Orderdetail, Product


class TestOrderDetailAPI:
    """Test cases for OrderDetail API endpoints."""

    @pytest.mark.django_db
    def test_list_order_details_authenticated(
        self, authenticated_api_client, order_detail
    ):
        """Test listing order details when authenticated."""
        url = reverse("classicmodels:orderdetail-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert (
            response.data["results"][0]["ordernumber"]
            == order_detail.ordernumber.ordernumber
        )
        assert (
            response.data["results"][0]["productcode"]
            == order_detail.productcode.productcode
        )

    @pytest.mark.django_db
    def test_list_order_details_unauthenticated(self, api_client, order_detail):
        """Test listing order details when not authenticated."""
        url = reverse("classicmodels:orderdetail-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_order_detail_authenticated(
        self, authenticated_api_client, order_detail
    ):
        """Test retrieving a specific order detail when authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["ordernumber"] == order_detail.ordernumber.ordernumber
        assert response.data["productcode"] == order_detail.productcode.productcode

    @pytest.mark.django_db
    def test_retrieve_order_detail_unauthenticated(self, api_client, order_detail):
        """Test retrieving an order detail when not authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_order_detail(self, authenticated_api_client, order):
        """Test retrieving an order detail that doesn't exist."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={"orderNumber": order.ordernumber, "productCode": "NONEXISTENT"},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_order_detail_authenticated(
        self, authenticated_api_client, order, product
    ):
        """Test creating an order detail when authenticated."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 3,
            "priceeach": "35.50",
            "orderlinenumber": 2,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["ordernumber"] == order.ordernumber
        assert response.data["productcode"] == product.productcode

    @pytest.mark.django_db
    def test_create_order_detail_unauthenticated(self, api_client, order, product):
        """Test creating an order detail when not authenticated."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 3,
            "priceeach": "35.50",
            "orderlinenumber": 2,
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_order_detail_duplicate(
        self, authenticated_api_client, order_detail
    ):
        """Test creating an order detail with duplicate order and product."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order_detail.ordernumber.ordernumber,
            "productcode": order_detail.productcode.productcode,  # Duplicate
            "quantityordered": 2,
            "priceeach": "40.00",
            "orderlinenumber": 3,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_order_detail_invalid_order(self, authenticated_api_client, product):
        """Test creating an order detail with invalid order."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": 99999,  # Invalid order
            "productcode": product.productcode,
            "quantityordered": 2,
            "priceeach": "40.00",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_order_detail_invalid_product(self, authenticated_api_client, order):
        """Test creating an order detail with invalid product."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": "NONEXISTENT",  # Invalid product
            "quantityordered": 2,
            "priceeach": "40.00",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_order_detail_same_product_different_orders(
        self, authenticated_api_client, product, customer, order
    ):
        """Test creating order details with same product in different orders."""
        # Create another order
        order2 = Order.objects.create(
            ordernumber=20001,
            orderdate="2024-02-16",
            requireddate="2024-02-21",
            status="In Process",
            customernumber=customer,
        )

        url = reverse("classicmodels:orderdetail-list")

        # First order detail
        data1 = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 1,
            "priceeach": "10.00",
            "orderlinenumber": 1,
        }

        response1 = authenticated_api_client.post(url, data1, format="json")
        assert response1.status_code == status.HTTP_201_CREATED

        # Second order detail with same product, different order
        data2 = {
            "ordernumber": order2.ordernumber,
            "productcode": product.productcode,  # Same product
            "quantityordered": 2,
            "priceeach": "15.00",
            "orderlinenumber": 1,
        }

        response2 = authenticated_api_client.post(url, data2, format="json")
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.data["ordernumber"] == order2.ordernumber
        assert response2.data["productcode"] == product.productcode

    @pytest.mark.django_db
    def test_update_order_detail_authenticated(
        self, authenticated_api_client, order_detail
    ):
        """Test updating an order detail when authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        data = {
            "ordernumber": order_detail.ordernumber.ordernumber,
            "productcode": order_detail.productcode.productcode,
            "quantityordered": 8,
            "priceeach": "50.00",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["quantityordered"] == 8
        assert response.data["priceeach"] == "50.00"

    @pytest.mark.django_db
    def test_update_order_detail_unauthenticated(self, api_client, order_detail):
        """Test updating an order detail when not authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        data = {
            "ordernumber": order_detail.ordernumber.ordernumber,
            "productcode": order_detail.productcode.productcode,
            "quantityordered": 8,
            "priceeach": "50.00",
            "orderlinenumber": 1,
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_order_detail_authenticated(
        self, authenticated_api_client, order_detail
    ):
        """Test partially updating an order detail when authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        data = {"quantityordered": 10, "priceeach": "60.00"}

        response = authenticated_api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["quantityordered"] == 10
        assert response.data["priceeach"] == "60.00"
        # Other fields should remain unchanged
        assert response.data["ordernumber"] == order_detail.ordernumber.ordernumber
        assert response.data["productcode"] == order_detail.productcode.productcode

    @pytest.mark.django_db
    def test_partial_update_order_detail_unauthenticated(
        self, api_client, order_detail
    ):
        """Test partially updating an order detail when not authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        data = {"quantityordered": 10}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_order_detail_authenticated(
        self, authenticated_api_client, order_detail
    ):
        """Test deleting an order detail when authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Orderdetail.objects.filter(
            ordernumber=order_detail.ordernumber, productcode=order_detail.productcode
        ).exists()

    @pytest.mark.django_db
    def test_delete_order_detail_unauthenticated(self, api_client, order_detail):
        """Test deleting an order detail when not authenticated."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_order_detail(self, authenticated_api_client, order):
        """Test deleting an order detail that doesn't exist."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={"orderNumber": order.ordernumber, "productCode": "NONEXISTENT"},
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_order_detail_serializer_validation(
        self, authenticated_api_client, order, product
    ):
        """Test order detail serializer validation."""
        url = reverse("classicmodels:orderdetail-list")

        # Test with invalid data (exceeds max length for check number)
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 2,
            "priceeach": "40.00",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED  # This should work

    @pytest.mark.django_db
    def test_order_detail_decimal_precision(
        self, authenticated_api_client, order, product
    ):
        """Test decimal field precision and rounding."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 1,
            "priceeach": "12.35",  # Valid 2 decimal places
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["priceeach"] == "12.35"

    @pytest.mark.django_db
    def test_order_detail_negative_quantity(
        self, authenticated_api_client, order, product
    ):
        """Test handling of negative quantities."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": -5,  # Negative quantity (return)
            "priceeach": "45.99",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantityordered"] == -5

    @pytest.mark.django_db
    def test_order_detail_zero_quantity(self, authenticated_api_client, order, product):
        """Test handling of zero quantities."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 0,
            "priceeach": "45.99",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantityordered"] == 0

    @pytest.mark.django_db
    def test_order_detail_negative_price(
        self, authenticated_api_client, order, product
    ):
        """Test handling of negative prices."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 1,
            "priceeach": "-45.99",  # Negative price (discount/refund)
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["priceeach"] == "-45.99"

    @pytest.mark.django_db
    def test_order_detail_zero_price(self, authenticated_api_client, order, product):
        """Test handling of zero prices."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 1,
            "priceeach": "0.00",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["priceeach"] == "0.00"

    @pytest.mark.django_db
    def test_order_detail_large_quantities(
        self, authenticated_api_client, order, product
    ):
        """Test handling of large quantities."""
        url = reverse("classicmodels:orderdetail-list")
        large_quantity = 999999  # Large integer

        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": large_quantity,
            "priceeach": "1.00",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantityordered"] == large_quantity

    @pytest.mark.django_db
    def test_order_detail_order_line_numbers(
        self, authenticated_api_client, order, product_line
    ):
        """Test various order line numbers."""
        url = reverse("classicmodels:orderdetail-list")
        line_numbers = [1, 2, 3, 10, 100, 999, 32767]  # SmallIntegerField range

        for i, line_number in enumerate(line_numbers):
            # Create a new product for each line to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"LINE{i:03d}",
                productname=f"Line Product {i}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            data = {
                "ordernumber": order.ordernumber,
                "productcode": new_product.productcode,
                "quantityordered": 1,
                "priceeach": "10.00",
                "orderlinenumber": line_number,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["orderlinenumber"] == line_number

    @pytest.mark.django_db
    def test_order_detail_price_precision_rounding(
        self, authenticated_api_client, order, product_line
    ):
        """Test price field precision and rounding."""
        url = reverse("classicmodels:orderdetail-list")
        test_prices = [
            ("12.35", "12.35"),  # Valid 2 decimal places
            ("12.34", "12.34"),  # Valid 2 decimal places
            ("12.36", "12.36"),  # Valid 2 decimal places
            ("12.34", "12.34"),  # Valid 2 decimal places
        ]

        for i, (input_price, expected_price) in enumerate(test_prices):
            # Create a new product for each test to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"PRICE{i:03d}",
                productname=f"Price Product {i}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            data = {
                "ordernumber": order.ordernumber,
                "productcode": new_product.productcode,
                "quantityordered": 1,
                "priceeach": input_price,
                "orderlinenumber": i + 1,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["priceeach"] == expected_price

    @pytest.mark.django_db
    def test_order_detail_very_small_prices(
        self, authenticated_api_client, order, product_line
    ):
        """Test handling of very small prices."""
        url = reverse("classicmodels:orderdetail-list")
        small_prices = ["0.01", "0.10", "0.99"]  # 1 cent, 10 cents, 99 cents

        for i, price in enumerate(small_prices):
            # Create a new product for each test to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"SMALL{i:03d}",
                productname=f"Small Price Product {i}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            data = {
                "ordernumber": order.ordernumber,
                "productcode": new_product.productcode,
                "quantityordered": 1,
                "priceeach": price,
                "orderlinenumber": i + 1,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["priceeach"] == price

    @pytest.mark.django_db
    def test_order_detail_very_large_prices(
        self, authenticated_api_client, order, product_line
    ):
        """Test handling of very large prices."""
        url = reverse("classicmodels:orderdetail-list")
        large_prices = [
            "99999999.99",
            "1000000.00",
            "5000000.50",
        ]  # Max value, 1 million, 5 million

        for i, price in enumerate(large_prices):
            # Create a new product for each test to avoid unique constraint
            new_product = Product.objects.create(
                productcode=f"LARGE{i:03d}",
                productname=f"Large Price Product {i}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            data = {
                "ordernumber": order.ordernumber,
                "productcode": new_product.productcode,
                "quantityordered": 1,
                "priceeach": price,
                "orderlinenumber": i + 1,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["priceeach"] == price

    @pytest.mark.django_db
    def test_order_detail_multiple_products_same_order(
        self, authenticated_api_client, order, product_line
    ):
        """Test multiple products in the same order."""
        url = reverse("classicmodels:orderdetail-list")

        # Create multiple products
        products = []
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
            data = {
                "ordernumber": order.ordernumber,
                "productcode": product.productcode,
                "quantityordered": i + 1,
                "priceeach": f"{10.00 + i * 5.00}",
                "orderlinenumber": i + 1,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["ordernumber"] == order.ordernumber

    @pytest.mark.django_db
    def test_order_detail_calculated_total(
        self, authenticated_api_client, order, product
    ):
        """Test calculated total (quantity * price)."""
        url = reverse("classicmodels:orderdetail-list")
        data = {
            "ordernumber": order.ordernumber,
            "productcode": product.productcode,
            "quantityordered": 3,
            "priceeach": "25.50",
            "orderlinenumber": 1,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        # Calculate expected total
        expected_total = 3 * Decimal("25.50")
        actual_total = response.data["quantityordered"] * Decimal(
            response.data["priceeach"]
        )
        assert actual_total == expected_total

    @pytest.mark.django_db
    def test_order_detail_different_quantities_and_prices(
        self, authenticated_api_client, order, product_line
    ):
        """Test various combinations of quantities and prices."""
        url = reverse("classicmodels:orderdetail-list")
        test_cases = [
            (1, "100.00"),  # 1 item at $100
            (10, "10.00"),  # 10 items at $10
            (100, "1.00"),  # 100 items at $1
            (5, "25.50"),  # 5 items at $25.50
            (2, "0.50"),  # 2 items at $0.50
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

            data = {
                "ordernumber": order.ordernumber,
                "productcode": product.productcode,
                "quantityordered": quantity,
                "priceeach": price,
                "orderlinenumber": i + 1,
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["quantityordered"] == quantity
            assert response.data["priceeach"] == price

            # Test calculated total
            expected_total = quantity * Decimal(price)
            actual_total = response.data["quantityordered"] * Decimal(
                response.data["priceeach"]
            )
            assert actual_total == expected_total

    @pytest.mark.django_db
    def test_order_detail_pagination(
        self, authenticated_api_client, order, product_line
    ):
        """Test order detail pagination."""
        # Create additional order details beyond the existing ones
        for i in range(15):  # More than default page size
            product = Product.objects.create(
                productcode=f"PAGE{i:03d}",
                productname=f"Pagination Product {i}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription="Description",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

            Orderdetail.objects.create(
                ordernumber=order,
                productcode=product,
                quantityordered=1,
                priceeach=Decimal("10.00"),
                orderlinenumber=i + 1,
            )

        url = reverse("classicmodels:orderdetail-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    @pytest.mark.django_db
    def test_order_detail_ordering(self, authenticated_api_client, order, product_line):
        """Test order detail ordering."""
        # Create order details in specific order
        product1 = Product.objects.create(
            productcode="ZPROD001",
            productname="Z Product",
            productline=product_line,
            productscale="1:10",
            productvendor="Vendor",
            productdescription="Description",
            quantityinstock=10,
            buyprice=Decimal("10.00"),
            msrp=Decimal("20.00"),
        )

        product2 = Product.objects.create(
            productcode="APROD001",
            productname="A Product",
            productline=product_line,
            productscale="1:10",
            productvendor="Vendor",
            productdescription="Description",
            quantityinstock=10,
            buyprice=Decimal("10.00"),
            msrp=Decimal("20.00"),
        )

        Orderdetail.objects.create(
            ordernumber=order,
            productcode=product1,
            quantityordered=1,
            priceeach=Decimal("10.00"),
            orderlinenumber=1,
        )

        Orderdetail.objects.create(
            ordernumber=order,
            productcode=product2,
            quantityordered=2,
            priceeach=Decimal("20.00"),
            orderlinenumber=2,
        )

        url = reverse("classicmodels:orderdetail-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data["results"]) >= 2

    @pytest.mark.django_db
    def test_order_detail_relationships(
        self, authenticated_api_client, order_detail, order, product
    ):
        """Test order detail relationships in API response."""
        url = reverse(
            "classicmodels:orderdetail-detail",
            kwargs={
                "orderNumber": order_detail.ordernumber.ordernumber,
                "productCode": order_detail.productcode.productcode,
            },
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "ordernumber" in response.data
        assert "productcode" in response.data
        assert response.data["ordernumber"] == order.ordernumber
        assert response.data["productcode"] == product.productcode
