"""
Tests for Product API endpoints.
"""

from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from classicmodels.models import Product


class TestProductAPI:
    """Test cases for Product API endpoints."""

    @pytest.mark.django_db
    def test_list_products_authenticated(self, authenticated_api_client, product):
        """Test listing products when authenticated."""
        url = reverse("classicmodels:product-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["productcode"] == product.productcode

    @pytest.mark.django_db
    def test_list_products_unauthenticated(self, api_client, product):
        """Test listing products when not authenticated."""
        url = reverse("classicmodels:product-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_product_authenticated(self, authenticated_api_client, product):
        """Test retrieving a specific product when authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["productcode"] == product.productcode
        assert response.data["productname"] == product.productname

    @pytest.mark.django_db
    def test_retrieve_product_unauthenticated(self, api_client, product):
        """Test retrieving a product when not authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_product(self, authenticated_api_client):
        """Test retrieving a product that doesn't exist."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": "NONEXISTENT"}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_product_authenticated(self, authenticated_api_client, product_line):
        """Test creating a product when authenticated."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": "NEW001",
            "productname": "New Product",
            "productline": product_line.productline,
            "productscale": "1:12",
            "productvendor": "New Vendor",
            "productdescription": "A new product for testing",
            "quantityinstock": 50,
            "buyprice": "25.50",
            "msrp": "45.99",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["productcode"] == "NEW001"
        assert response.data["productname"] == "New Product"
        assert response.data["productline"] == product_line.productline

    @pytest.mark.django_db
    def test_create_product_unauthenticated(self, api_client, product_line):
        """Test creating a product when not authenticated."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": "NEW001",
            "productname": "New Product",
            "productline": product_line.productline,
            "productscale": "1:12",
            "productvendor": "New Vendor",
            "productdescription": "A new product for testing",
            "quantityinstock": 50,
            "buyprice": "25.50",
            "msrp": "45.99",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_product_duplicate_code(self, authenticated_api_client, product):
        """Test creating a product with duplicate product code."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": product.productcode,  # Duplicate
            "productname": "Duplicate Product",
            "productline": product.productline.productline,
            "productscale": "1:12",
            "productvendor": "Vendor",
            "productdescription": "Duplicate product",
            "quantityinstock": 10,
            "buyprice": "10.00",
            "msrp": "20.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_product_invalid_product_line(self, authenticated_api_client):
        """Test creating a product with invalid product line."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": "INVALID001",
            "productname": "Invalid Product",
            "productline": "NONEXISTENT",  # Invalid product line
            "productscale": "1:12",
            "productvendor": "Vendor",
            "productdescription": "Invalid product",
            "quantityinstock": 10,
            "buyprice": "10.00",
            "msrp": "20.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_product_minimal_data(self, authenticated_api_client, product_line):
        """Test creating a product with minimal required data."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": "MIN001",
            "productname": "Minimal Product",
            "productline": product_line.productline,
            "productscale": "1:10",
            "productvendor": "Vendor",
            "productdescription": "Minimal description",
            "quantityinstock": 0,
            "buyprice": "0.00",
            "msrp": "0.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["productcode"] == "MIN001"
        assert response.data["quantityinstock"] == 0
        assert response.data["buyprice"] == "0.00"

    @pytest.mark.django_db
    def test_update_product_authenticated(self, authenticated_api_client, product):
        """Test updating a product when authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        data = {
            "productcode": product.productcode,
            "productname": "Updated Product",
            "productline": product.productline.productline,
            "productscale": "1:18",
            "productvendor": "Updated Vendor",
            "productdescription": "Updated description",
            "quantityinstock": 200,
            "buyprice": "30.00",
            "msrp": "55.00",
        }

        response = authenticated_api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["productname"] == "Updated Product"
        assert response.data["productscale"] == "1:18"
        assert response.data["quantityinstock"] == 200

    @pytest.mark.django_db
    def test_update_product_unauthenticated(self, api_client, product):
        """Test updating a product when not authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        data = {
            "productcode": product.productcode,
            "productname": "Updated Product",
            "productline": product.productline.productline,
            "productscale": "1:18",
            "productvendor": "Updated Vendor",
            "productdescription": "Updated description",
            "quantityinstock": 200,
            "buyprice": "30.00",
            "msrp": "55.00",
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_product_authenticated(
        self, authenticated_api_client, product
    ):
        """Test partially updating a product when authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        data = {"productname": "Partially Updated Product", "quantityinstock": 150}

        response = authenticated_api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["productname"] == "Partially Updated Product"
        assert response.data["quantityinstock"] == 150
        # Other fields should remain unchanged
        assert response.data["productcode"] == product.productcode

    @pytest.mark.django_db
    def test_partial_update_product_unauthenticated(self, api_client, product):
        """Test partially updating a product when not authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        data = {"productname": "Partially Updated Product"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_product_authenticated(self, authenticated_api_client, product):
        """Test deleting a product when authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(productcode=product.productcode).exists()

    @pytest.mark.django_db
    def test_delete_product_unauthenticated(self, api_client, product):
        """Test deleting a product when not authenticated."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_product(self, authenticated_api_client):
        """Test deleting a product that doesn't exist."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": "NONEXISTENT"}
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_product_serializer_validation(
        self, authenticated_api_client, product_line
    ):
        """Test product serializer validation."""
        url = reverse("classicmodels:product-list")

        # Test with invalid data (exceeds max length)
        data = {
            "productcode": "x" * 16,  # Exceeds max_length=15
            "productname": "Valid Product",
            "productline": product_line.productline,
            "productscale": "1:10",
            "productvendor": "Vendor",
            "productdescription": "Description",
            "quantityinstock": 10,
            "buyprice": "10.00",
            "msrp": "20.00",
        }

        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_product_decimal_precision(self, authenticated_api_client, product_line):
        """Test decimal field precision and rounding."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": "DECIMAL001",
            "productname": "Decimal Test Product",
            "productline": product_line.productline,
            "productscale": "1:10",
            "productvendor": "Vendor",
            "productdescription": "Description",
            "quantityinstock": 10,
            "buyprice": "12.35",  # Valid 2 decimal places
            "msrp": "24.68",  # Valid 2 decimal places
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["buyprice"] == "12.35"
        assert response.data["msrp"] == "24.68"

    @pytest.mark.django_db
    def test_product_unicode_handling(self, authenticated_api_client, product_line):
        """Test handling of unicode characters in product."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": "UNICODE001",
            "productname": "Product with émojis 🚀 and accents café",
            "productline": product_line.productline,
            "productscale": "1:10",
            "productvendor": "Vendor with émojis 🏢",
            "productdescription": "Description with émojis 🚀 and accents café",
            "quantityinstock": 10,
            "buyprice": "10.00",
            "msrp": "20.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "émojis" in response.data["productname"]
        assert "🚀" in response.data["productname"]
        assert "café" in response.data["productname"]

    @pytest.mark.django_db
    def test_product_negative_values(self, authenticated_api_client, product_line):
        """Test handling of negative values in numeric fields."""
        url = reverse("classicmodels:product-list")
        data = {
            "productcode": "NEG001",
            "productname": "Negative Test Product",
            "productline": product_line.productline,
            "productscale": "1:10",
            "productvendor": "Vendor",
            "productdescription": "Description",
            "quantityinstock": -10,  # Negative quantity
            "buyprice": "-10.00",  # Negative price
            "msrp": "-20.00",  # Negative MSRP
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantityinstock"] == -10
        assert response.data["buyprice"] == "-10.00"
        assert response.data["msrp"] == "-20.00"

    @pytest.mark.django_db
    def test_product_large_text_description(
        self, authenticated_api_client, product_line
    ):
        """Test handling of large text in product description."""
        url = reverse("classicmodels:product-list")
        large_description = "x" * 10000  # Large text

        data = {
            "productcode": "LARGE001",
            "productname": "Large Description Product",
            "productline": product_line.productline,
            "productscale": "1:10",
            "productvendor": "Vendor",
            "productdescription": large_description,
            "quantityinstock": 10,
            "buyprice": "10.00",
            "msrp": "20.00",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["productdescription"]) == 10000

    @pytest.mark.django_db
    def test_product_scale_variations(self, authenticated_api_client, product_line):
        """Test different product scale formats."""
        url = reverse("classicmodels:product-list")
        scales = [
            "1:10",
            "1:12",
            "1:18",
            "1:24",
            "1:32",
            "1:43",
            "1:50",
            "1:72",
            "1:100",
            "1:144",
        ]

        for i, scale in enumerate(scales):
            data = {
                "productcode": f"SCALE{i:03d}",
                "productname": f"Scale {scale} Product",
                "productline": product_line.productline,
                "productscale": scale,
                "productvendor": "Vendor",
                "productdescription": "Description",
                "quantityinstock": 10,
                "buyprice": "10.00",
                "msrp": "20.00",
            }

            response = authenticated_api_client.post(url, data, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            assert response.data["productscale"] == scale

    @pytest.mark.django_db
    def test_product_pagination(self, authenticated_api_client, multiple_products):
        """Test product pagination."""
        # Create additional products beyond the existing ones
        for i in range(15):  # More than default page size
            Product.objects.create(
                productcode=f"PAGE{i:03d}",
                productname=f"Pagination Product {i}",
                productline=multiple_products[0].productline,
                productscale="1:10",
                productvendor="Vendor",
                productdescription=f"Description for product {i}",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

        url = reverse("classicmodels:product-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    @pytest.mark.django_db
    def test_product_ordering(self, authenticated_api_client, product_line):
        """Test product ordering."""
        # Create products in specific order
        Product.objects.create(
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
        Product.objects.create(
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

        url = reverse("classicmodels:product-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data["results"]) >= 2

    @pytest.mark.django_db
    def test_product_relationships(self, authenticated_api_client, product):
        """Test product relationships in API response."""
        url = reverse(
            "classicmodels:product-detail", kwargs={"productcode": product.productcode}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "productline" in response.data
        assert response.data["productline"] == product.productline.productline
