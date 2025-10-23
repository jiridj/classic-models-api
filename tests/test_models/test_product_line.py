"""
Tests for ProductLine model.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from classicmodels.models import ProductLine


class TestProductLineModel:
    """Test cases for ProductLine model."""

    @pytest.mark.django_db
    def test_product_line_creation(self):
        """Test creating a product line with all fields."""
        product_line = ProductLine.objects.create(
            productline="Test Line",
            textdescription="Test description",
            htmldescription="<p>Test HTML</p>",
            image=b"test_image_data",
        )

        assert product_line.productline == "Test Line"
        assert product_line.textdescription == "Test description"
        assert product_line.htmldescription == "<p>Test HTML</p>"
        assert product_line.image == b"test_image_data"

    @pytest.mark.django_db
    def test_product_line_creation_minimal(self):
        """Test creating a product line with only required fields."""
        product_line = ProductLine.objects.create(productline="Minimal Line")

        assert product_line.productline == "Minimal Line"
        assert product_line.textdescription is None
        assert product_line.htmldescription is None
        assert product_line.image is None

    @pytest.mark.django_db
    def test_product_line_string_representation(self):
        """Test the string representation of ProductLine."""
        product_line = ProductLine.objects.create(productline="Test Line")

        assert str(product_line) == "Test Line"

    @pytest.mark.django_db
    def test_product_line_primary_key(self):
        """Test that productline is the primary key."""
        product_line = ProductLine.objects.create(productline="PK Test")

        assert product_line.pk == "PK Test"

    @pytest.mark.django_db
    def test_product_line_max_length_constraints(self):
        """Test field max length constraints."""
        # Test productline max length (50)
        with pytest.raises(ValidationError):
            product_line = ProductLine(productline="x" * 51)  # Exceeds max_length=50
            product_line.full_clean()

    @pytest.mark.django_db
    def test_product_line_blank_fields(self):
        """Test that optional fields can be blank."""
        product_line = ProductLine.objects.create(
            productline="Blank Test",
            textdescription="",  # Empty string should be allowed
            htmldescription="",  # Empty string should be allowed
        )

        assert product_line.textdescription == ""
        assert product_line.htmldescription == ""

    @pytest.mark.django_db
    def test_product_line_null_fields(self):
        """Test that optional fields can be null."""
        product_line = ProductLine.objects.create(
            productline="Null Test",
            textdescription=None,
            htmldescription=None,
            image=None,
        )

        assert product_line.textdescription is None
        assert product_line.htmldescription is None
        assert product_line.image is None

    @pytest.mark.django_db
    def test_product_line_unique_constraint(self):
        """Test that productline must be unique."""
        ProductLine.objects.create(productline="Unique Test")

        with pytest.raises(IntegrityError):
            ProductLine.objects.create(productline="Unique Test")

    @pytest.mark.django_db
    def test_product_line_meta_options(self):
        """Test model meta options."""
        assert ProductLine._meta.managed is True  # Overridden for testing
        assert ProductLine._meta.db_table == "productlines"

    @pytest.mark.django_db
    def test_product_line_field_attributes(self):
        """Test field attributes and constraints."""
        # Test productline field
        productline_field = ProductLine._meta.get_field("productline")
        assert productline_field.max_length == 50
        assert productline_field.primary_key is True

        # Test textdescription field
        textdescription_field = ProductLine._meta.get_field("textdescription")
        assert textdescription_field.max_length == 4000
        assert textdescription_field.blank is True
        assert textdescription_field.null is True

        # Test htmldescription field
        htmldescription_field = ProductLine._meta.get_field("htmldescription")
        assert htmldescription_field.blank is True
        assert htmldescription_field.null is True

        # Test image field
        image_field = ProductLine._meta.get_field("image")
        assert image_field.blank is True
        assert image_field.null is True

    @pytest.mark.django_db
    def test_product_line_relationships(self, product):
        """Test relationships with other models."""
        # Test reverse relationship with Product
        assert product.productline == product.productline
        assert product in product.productline.product_set.all()

    @pytest.mark.django_db
    def test_product_line_ordering(self):
        """Test default ordering if any."""
        ProductLine.objects.create(productline="Z Line")
        ProductLine.objects.create(productline="A Line")
        ProductLine.objects.create(productline="M Line")

        product_lines = list(ProductLine.objects.all())
        # Since no ordering is defined, order is not guaranteed
        assert len(product_lines) == 3

    @pytest.mark.django_db
    def test_product_line_unicode_handling(self):
        """Test handling of unicode characters."""
        product_line = ProductLine.objects.create(
            productline="Unicode Test 测试",
            textdescription="Description with émojis 🚀 and accents café",
            htmldescription="<p>HTML with émojis 🚀 and accents café</p>",
        )

        assert product_line.productline == "Unicode Test 测试"
        assert "émojis" in product_line.textdescription
        assert "🚀" in product_line.textdescription
        assert "café" in product_line.textdescription

    @pytest.mark.django_db
    def test_product_line_large_data(self):
        """Test handling of large data in text fields."""
        large_text = "x" * 4000  # Max length for textdescription
        large_html = "<p>" + "x" * 4000 + "</p>"

        product_line = ProductLine.objects.create(
            productline="Large Data Test",
            textdescription=large_text,
            htmldescription=large_html,
        )

        assert len(product_line.textdescription) == 4000
        assert len(product_line.htmldescription) == 4007  # 4000 + '<p></p>' (3 chars)

    @pytest.mark.django_db
    def test_product_line_binary_data(self):
        """Test handling of binary data in image field."""
        binary_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"

        product_line = ProductLine.objects.create(
            productline="Binary Test", image=binary_data
        )

        assert product_line.image == binary_data
        assert isinstance(product_line.image, bytes)
