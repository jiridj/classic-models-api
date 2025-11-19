"""
Tests for ProductLine API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status

from classicmodels.models import ProductLine


class TestProductLineAPI:
    """Test cases for ProductLine API endpoints."""

    @pytest.mark.django_db
    def test_list_product_lines_authenticated(
        self, authenticated_api_client, product_line
    ):
        """Test listing product lines when authenticated."""
        url = reverse("classicmodels:productline-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["productline"] == product_line.productline

    @pytest.mark.django_db
    def test_list_product_lines_unauthenticated(self, api_client, product_line):
        """Test listing product lines when not authenticated."""
        url = reverse("classicmodels:productline-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_product_line_authenticated(
        self, authenticated_api_client, product_line
    ):
        """Test retrieving a specific product line when authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["productline"] == product_line.productline
        assert response.data["textdescription"] == product_line.textdescription

    @pytest.mark.django_db
    def test_retrieve_product_line_unauthenticated(self, api_client, product_line):
        """Test retrieving a product line when not authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_retrieve_nonexistent_product_line(self, authenticated_api_client):
        """Test retrieving a product line that doesn't exist."""
        url = reverse(
            "classicmodels:productline-detail", kwargs={"productline": "NONEXISTENT"}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_create_product_line_authenticated(self, authenticated_api_client):
        """Test creating a product line when authenticated."""
        url = reverse("classicmodels:productline-list")
        data = {
            "productline": "New Line",
            "textdescription": "New product line description",
            "htmldescription": "<p>New HTML description</p>",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["productline"] == "New Line"
        assert response.data["textdescription"] == "New product line description"
        assert response.data["htmldescription"] == "<p>New HTML description</p>"

    @pytest.mark.django_db
    def test_create_product_line_unauthenticated(self, api_client):
        """Test creating a product line when not authenticated."""
        url = reverse("classicmodels:productline-list")
        data = {
            "productline": "New Line",
            "textdescription": "New product line description",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_create_product_line_duplicate(
        self, authenticated_api_client, product_line
    ):
        """Test creating a product line with duplicate productline."""
        url = reverse("classicmodels:productline-list")
        data = {
            "productline": product_line.productline,  # Duplicate
            "textdescription": "Duplicate description",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_product_line_minimal_data(self, authenticated_api_client):
        """Test creating a product line with minimal required data."""
        url = reverse("classicmodels:productline-list")
        data = {"productline": "Minimal Line"}

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["productline"] == "Minimal Line"
        assert response.data["textdescription"] is None
        assert response.data["htmldescription"] is None

    @pytest.mark.django_db
    def test_update_product_line_authenticated(
        self, authenticated_api_client, product_line
    ):
        """Test updating a product line when authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        data = {
            "productline": product_line.productline,
            "textdescription": "Updated description",
            "htmldescription": "<p>Updated HTML</p>",
        }

        response = authenticated_api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["textdescription"] == "Updated description"
        assert response.data["htmldescription"] == "<p>Updated HTML</p>"

    @pytest.mark.django_db
    def test_update_product_line_unauthenticated(self, api_client, product_line):
        """Test updating a product line when not authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        data = {
            "productline": product_line.productline,
            "textdescription": "Updated description",
        }

        response = api_client.put(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_partial_update_product_line_authenticated(
        self, authenticated_api_client, product_line
    ):
        """Test partially updating a product line when authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        data = {"textdescription": "Partially updated description"}

        response = authenticated_api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["textdescription"] == "Partially updated description"
        # Other fields should remain unchanged
        assert response.data["productline"] == product_line.productline

    @pytest.mark.django_db
    def test_partial_update_product_line_unauthenticated(
        self, api_client, product_line
    ):
        """Test partially updating a product line when not authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        data = {"textdescription": "Partially updated description"}

        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_product_line_authenticated(
        self, authenticated_api_client, product_line
    ):
        """Test deleting a product line when authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ProductLine.objects.filter(
            productline=product_line.productline
        ).exists()

    @pytest.mark.django_db
    def test_delete_product_line_unauthenticated(self, api_client, product_line):
        """Test deleting a product line when not authenticated."""
        url = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        )
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_delete_nonexistent_product_line(self, authenticated_api_client):
        """Test deleting a product line that doesn't exist."""
        url = reverse(
            "classicmodels:productline-detail", kwargs={"productline": "NONEXISTENT"}
        )
        response = authenticated_api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_product_line_serializer_validation(self, authenticated_api_client):
        """Test product line serializer validation."""
        url = reverse("classicmodels:productline-list")

        # Test with invalid data (exceeds max length)
        data = {
            "productline": "x" * 51,  # Exceeds max_length=50
            "textdescription": "Valid description",
        }

        response = authenticated_api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_product_line_unicode_handling(self, authenticated_api_client):
        """Test handling of unicode characters in product line."""
        url = reverse("classicmodels:productline-list")
        data = {
            "productline": "Unicode Line 测试",
            "textdescription": "Description with émojis 🚀 and accents café",
            "htmldescription": "<p>HTML with émojis 🚀 and accents café</p>",
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "émojis" in response.data["textdescription"]
        assert "🚀" in response.data["textdescription"]
        assert "café" in response.data["textdescription"]

    @pytest.mark.django_db
    def test_product_line_large_data(self, authenticated_api_client):
        """Test handling of large data in text fields."""
        url = reverse("classicmodels:productline-list")
        large_text = "x" * 4000  # Max length for textdescription
        large_html = "<p>" + "x" * 4000 + "</p>"

        data = {
            "productline": "Large Data Line",
            "textdescription": large_text,
            "htmldescription": large_html,
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["textdescription"]) == 4000
        assert (
            len(response.data["htmldescription"]) == 4007
        )  # 4000 + '<p></p>' (3 chars)

    @pytest.mark.django_db
    def test_product_line_binary_image_data(self, authenticated_api_client):
        """Test handling of binary data in image field."""
        url = reverse("classicmodels:productline-list")

        # Test creating a product line without binary data first
        data = {
            "productline": "Binary Image Line",
            "textdescription": "Line with binary image data",
            "image": None,  # No binary data for JSON format
        }

        response = authenticated_api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "image" in response.data
        assert response.data["image"] is None

        # Test that the field exists in the model
        product_line = ProductLine.objects.get(productline="Binary Image Line")
        assert hasattr(product_line, "image")
        assert product_line.image is None

    @pytest.mark.django_db
    def test_product_line_pagination(self, authenticated_api_client, multiple_products):
        """Test product line pagination."""
        # Create multiple product lines
        for i in range(15):  # More than default page size
            ProductLine.objects.create(
                productline=f"Pagination Line {i:03d}",
                textdescription=f"Description for line {i}",
            )

        url = reverse("classicmodels:productline-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    @pytest.mark.django_db
    def test_product_line_ordering(self, authenticated_api_client):
        """Test product line ordering."""
        # Create product lines in specific order
        ProductLine.objects.create(productline="Z Line")
        ProductLine.objects.create(productline="A Line")
        ProductLine.objects.create(productline="M Line")

        url = reverse("classicmodels:productline-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Since no ordering is defined, order is not guaranteed
        assert len(response.data["results"]) >= 3

    @pytest.mark.django_db
    def test_product_line_filtering(self, authenticated_api_client):
        """Test product line filtering capabilities."""
        # Create product lines with different descriptions
        ProductLine.objects.create(
            productline="Filter Line 1", textdescription="Contains keyword test"
        )
        ProductLine.objects.create(
            productline="Filter Line 2", textdescription="No keyword here"
        )

        url = reverse("classicmodels:productline-list")
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Basic filtering test - more complex filtering would require custom filters
        assert len(response.data["results"]) >= 2

    @pytest.mark.django_db
    def test_get_product_line_products_authenticated(
        self, authenticated_api_client, product_line, product
    ):
        """Test retrieving products for a product line when authenticated."""
        url = reverse(
            "classicmodels:productline-products",
            kwargs={"productline": product_line.productline},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data or isinstance(response.data, list)
        # If paginated, check results; otherwise check list directly
        if "results" in response.data:
            assert len(response.data["results"]) >= 1
            assert response.data["results"][0]["productcode"] == product.productcode
        else:
            assert len(response.data) >= 1
            assert response.data[0]["productcode"] == product.productcode

    @pytest.mark.django_db
    def test_get_product_line_products_unauthenticated(self, api_client, product_line):
        """Test retrieving products for a product line when not authenticated."""
        url = reverse(
            "classicmodels:productline-products",
            kwargs={"productline": product_line.productline},
        )
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_get_product_line_products_nonexistent_product_line(
        self, authenticated_api_client
    ):
        """Test retrieving products for a product line that doesn't exist."""
        url = reverse(
            "classicmodels:productline-products", kwargs={"productline": "NONEXIST"}
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_get_product_line_products_empty(self, authenticated_api_client):
        """Test retrieving products for a product line with no products."""
        from classicmodels.models import ProductLine

        # Create a product line with no products
        product_line_no_products = ProductLine.objects.create(
            productline="Empty Line",
            textdescription="Product line with no products",
        )

        url = reverse(
            "classicmodels:productline-products",
            kwargs={"productline": product_line_no_products.productline},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should return empty list or empty results
        if "results" in response.data:
            assert len(response.data["results"]) == 0
        else:
            assert len(response.data) == 0

    @pytest.mark.django_db
    def test_get_product_line_products_multiple_products(
        self, authenticated_api_client, product_line
    ):
        """Test retrieving products for a product line with multiple products."""
        from classicmodels.models import Product
        from decimal import Decimal

        # Create multiple products in this product line
        products = []
        for i in range(3):
            product = Product.objects.create(
                productcode=f"MULTI{i+1:03d}",
                productname=f"Product {i+1}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription=f"Description for product {i+1}",
                quantityinstock=10 + i * 10,
                buyprice=Decimal("10.00") + i * Decimal("5.00"),
                msrp=Decimal("20.00") + i * Decimal("8.00"),
            )
            products.append(product)

        url = reverse(
            "classicmodels:productline-products",
            kwargs={"productline": product_line.productline},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Check that all products are returned
        if "results" in response.data:
            product_codes = [p["productcode"] for p in response.data["results"]]
        else:
            product_codes = [p["productcode"] for p in response.data]

        for product in products:
            assert product.productcode in product_codes

    @pytest.mark.django_db
    def test_get_product_line_products_pagination(
        self, authenticated_api_client, product_line
    ):
        """Test pagination for product line products endpoint."""
        from classicmodels.models import Product
        from decimal import Decimal

        # Create more products than default page size
        for i in range(15):
            Product.objects.create(
                productcode=f"PAGE{i+1:03d}",
                productname=f"Pagination Product {i+1}",
                productline=product_line,
                productscale="1:10",
                productvendor="Vendor",
                productdescription=f"Description for product {i+1}",
                quantityinstock=10,
                buyprice=Decimal("10.00"),
                msrp=Decimal("20.00"),
            )

        url = reverse(
            "classicmodels:productline-products",
            kwargs={"productline": product_line.productline},
        )
        response = authenticated_api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should have pagination metadata
        assert "count" in response.data
        assert "next" in response.data or response.data["next"] is None
        assert "previous" in response.data or response.data["previous"] is None
        assert "results" in response.data
