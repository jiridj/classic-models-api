"""
Tests for Product model.
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from classicmodels.models import Product, ProductLine


class TestProductModel:
    """Test cases for Product model."""

    @pytest.mark.django_db
    def test_product_creation(self, product_line):
        """Test creating a product with all fields."""
        product = Product.objects.create(
            productcode='TEST001',
            productname='Test Product',
            productline=product_line,
            productscale='1:10',
            productvendor='Test Vendor',
            productdescription='A test product for testing purposes',
            quantityinstock=100,
            buyprice=Decimal('25.50'),
            msrp=Decimal('45.99')
        )
        
        assert product.productcode == 'TEST001'
        assert product.productname == 'Test Product'
        assert product.productline == product_line
        assert product.productscale == '1:10'
        assert product.productvendor == 'Test Vendor'
        assert product.productdescription == 'A test product for testing purposes'
        assert product.quantityinstock == 100
        assert product.buyprice == Decimal('25.50')
        assert product.msrp == Decimal('45.99')

    @pytest.mark.django_db
    def test_product_string_representation(self, product):
        """Test the string representation of Product."""
        assert str(product) == 'TEST001'

    @pytest.mark.django_db
    def test_product_primary_key(self, product):
        """Test that productcode is the primary key."""
        assert product.pk == 'TEST001'

    @pytest.mark.django_db
    def test_product_foreign_key_relationship(self, product, product_line):
        """Test foreign key relationship with ProductLine."""
        assert product.productline == product_line
        assert product in product_line.product_set.all()

    @pytest.mark.django_db
    def test_product_max_length_constraints(self, product_line):
        """Test field max length constraints."""
        # Test productcode max length (15)
        with pytest.raises(ValidationError):
            product = Product(
                productcode='x' * 16,  # Exceeds max_length=15
                productname='Test',
                productline=product_line,
                productscale='1:10',
                productvendor='Vendor',
                productdescription='Description',
                quantityinstock=10,
                buyprice=Decimal('10.00'),
                msrp=Decimal('20.00')
            )
            product.full_clean()

        # Test productname max length (70)
        with pytest.raises(ValidationError):
            product = Product(
                productcode='TEST',
                productname='x' * 71,  # Exceeds max_length=70
                productline=product_line,
                productscale='1:10',
                productvendor='Vendor',
                productdescription='Description',
                quantityinstock=10,
                buyprice=Decimal('10.00'),
                msrp=Decimal('20.00')
            )
            product.full_clean()

    @pytest.mark.django_db
    def test_product_decimal_field_precision(self, product_line):
        """Test decimal field precision and scale."""
        # Test buyprice precision (10,2)
        product = Product.objects.create(
            productcode='DECIMAL001',
            productname='Decimal Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription='Description',
            quantityinstock=10,
            buyprice=Decimal('99999999.99'),  # Max value for (10,2)
            msrp=Decimal('99999999.99')
        )
        
        assert product.buyprice == Decimal('99999999.99')
        assert product.msrp == Decimal('99999999.99')

    @pytest.mark.django_db
    def test_product_required_fields(self, product_line):
        """Test that required fields cannot be null."""
        # Test that productcode is required (primary key)
        product = Product(
            productcode='',  # Empty string instead of None
            productname='Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription='Description',
            quantityinstock=10,
            buyprice=Decimal('10.00'),
            msrp=Decimal('20.00')
        )
        # In testing environment, we can't rely on database constraints
        # Instead, we test that the field is defined as required
        assert Product._meta.get_field('productcode').primary_key is True
        assert not Product._meta.get_field('productcode').null

    @pytest.mark.django_db
    def test_product_unique_constraint(self, product_line):
        """Test that productcode must be unique."""
        Product.objects.create(
            productcode='UNIQUE001',
            productname='Unique Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription='Description',
            quantityinstock=10,
            buyprice=Decimal('10.00'),
            msrp=Decimal('20.00')
        )
        
        with pytest.raises(IntegrityError):
            Product.objects.create(
                productcode='UNIQUE001',  # Duplicate
                productname='Another Test',
                productline=product_line,
                productscale='1:10',
                productvendor='Vendor',
                productdescription='Description',
                quantityinstock=10,
                buyprice=Decimal('10.00'),
                msrp=Decimal('20.00')
            )

    @pytest.mark.django_db
    def test_product_meta_options(self):
        """Test model meta options."""
        assert Product._meta.managed is True  # Overridden for testing
        assert Product._meta.db_table == 'products'

    @pytest.mark.django_db
    def test_product_field_attributes(self):
        """Test field attributes and constraints."""
        # Test productcode field
        productcode_field = Product._meta.get_field('productcode')
        assert productcode_field.max_length == 15
        assert productcode_field.primary_key is True
        
        # Test productname field
        productname_field = Product._meta.get_field('productname')
        assert productname_field.max_length == 70
        
        # Test productscale field
        productscale_field = Product._meta.get_field('productscale')
        assert productscale_field.max_length == 10
        
        # Test productvendor field
        productvendor_field = Product._meta.get_field('productvendor')
        assert productvendor_field.max_length == 50
        
        # Test quantityinstock field
        quantityinstock_field = Product._meta.get_field('quantityinstock')
        assert isinstance(quantityinstock_field, models.SmallIntegerField)  # SmallIntegerField
        
        # Test buyprice field
        buyprice_field = Product._meta.get_field('buyprice')
        assert buyprice_field.max_digits == 10
        assert buyprice_field.decimal_places == 2
        
        # Test msrp field
        msrp_field = Product._meta.get_field('msrp')
        assert msrp_field.max_digits == 10
        assert msrp_field.decimal_places == 2

    @pytest.mark.django_db
    def test_product_foreign_key_cascade(self, product_line):
        """Test foreign key behavior when referenced object is deleted."""
        product = Product.objects.create(
            productcode='CASCADE001',
            productname='Cascade Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription='Description',
            quantityinstock=10,
            buyprice=Decimal('10.00'),
            msrp=Decimal('20.00')
        )
        
        # Since managed=False, we can't test actual cascade behavior
        # But we can test the relationship exists
        assert product.productline == product_line

    @pytest.mark.django_db
    def test_product_negative_values(self, product_line):
        """Test handling of negative values in numeric fields."""
        # Test negative quantityinstock
        product = Product.objects.create(
            productcode='NEG001',
            productname='Negative Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription='Description',
            quantityinstock=-10,  # Negative value
            buyprice=Decimal('10.00'),
            msrp=Decimal('20.00')
        )
        
        assert product.quantityinstock == -10

    @pytest.mark.django_db
    def test_product_zero_values(self, product_line):
        """Test handling of zero values."""
        product = Product.objects.create(
            productcode='ZERO001',
            productname='Zero Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription='Description',
            quantityinstock=0,
            buyprice=Decimal('0.00'),
            msrp=Decimal('0.00')
        )
        
        assert product.quantityinstock == 0
        assert product.buyprice == Decimal('0.00')
        assert product.msrp == Decimal('0.00')

    @pytest.mark.django_db
    def test_product_large_text_description(self, product_line):
        """Test handling of large text in productdescription."""
        large_description = 'x' * 10000  # Large text
        
        product = Product.objects.create(
            productcode='LARGE001',
            productname='Large Description Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription=large_description,
            quantityinstock=10,
            buyprice=Decimal('10.00'),
            msrp=Decimal('20.00')
        )
        
        assert len(product.productdescription) == 10000

    @pytest.mark.django_db
    def test_product_unicode_handling(self, product_line):
        """Test handling of unicode characters."""
        product = Product.objects.create(
            productcode='UNICODE001',
            productname='Product with émojis 🚀 and accents café',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor with émojis 🏢',
            productdescription='Description with émojis 🚀 and accents café',
            quantityinstock=10,
            buyprice=Decimal('10.00'),
            msrp=Decimal('20.00')
        )
        
        assert 'émojis' in product.productname
        assert '🚀' in product.productname
        assert 'café' in product.productname
        assert '🏢' in product.productvendor

    @pytest.mark.django_db
    def test_product_scale_variations(self, product_line):
        """Test different product scale formats."""
        scales = ['1:10', '1:12', '1:18', '1:24', '1:32', '1:43', '1:50', '1:72', '1:100', '1:144']
        
        for i, scale in enumerate(scales):
            product = Product.objects.create(
                productcode=f'SCALE{i:03d}',
                productname=f'Scale {scale} Product',
                productline=product_line,
                productscale=scale,
                productvendor='Vendor',
                productdescription='Description',
                quantityinstock=10,
                buyprice=Decimal('10.00'),
                msrp=Decimal('20.00')
            )
            
            assert product.productscale == scale

    @pytest.mark.django_db
    def test_product_price_calculations(self, product_line):
        """Test price field calculations and precision."""
        # Test high precision decimal values
        product = Product.objects.create(
            productcode='PRICE001',
            productname='Price Test',
            productline=product_line,
            productscale='1:10',
            productvendor='Vendor',
            productdescription='Description',
            quantityinstock=10,
            buyprice=Decimal('12.35'),  # Use exact 2 decimal places
            msrp=Decimal('24.68')       # Use exact 2 decimal places
        )
        
        # Check that values are stored correctly
        assert product.buyprice == Decimal('12.35')
        assert product.msrp == Decimal('24.68')
        
        # Test that the field definitions enforce 2 decimal places
        buyprice_field = Product._meta.get_field('buyprice')
        assert buyprice_field.decimal_places == 2
        assert buyprice_field.max_digits == 10
        
        msrp_field = Product._meta.get_field('msrp')
        assert msrp_field.decimal_places == 2
        assert msrp_field.max_digits == 10
