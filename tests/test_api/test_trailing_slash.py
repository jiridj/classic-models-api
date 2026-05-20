"""
Tests for optional trailing slash handling on API endpoints.
"""

import pytest
from django.urls import reverse
from rest_framework import status


def assert_optional_slash(client, path_with_slash, expected_status=status.HTTP_200_OK):
    """Both slash and no-slash forms must return the same status."""
    with_slash = client.get(path_with_slash)
    without_slash = client.get(path_with_slash.rstrip("/"))

    assert with_slash.status_code == expected_status, with_slash.data
    assert without_slash.status_code == expected_status, without_slash.data


@pytest.mark.django_db
class TestOptionalTrailingSlashV1:
    """All /api/v1/ routes accept URLs with or without a trailing slash."""

    def test_customer_list_and_detail(self, authenticated_api_client, customer):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:customer-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:customer-detail",
                kwargs={"customernumber": customer.customernumber},
            ),
        )

    def test_product_list_and_detail(self, authenticated_api_client, product):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:product-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:product-detail",
                kwargs={"productcode": product.productcode},
            ),
        )

    def test_product_line_list_and_detail(
        self, authenticated_api_client, product_line
    ):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:productline-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:productline-detail",
                kwargs={"productline": product_line.productline},
            ),
        )

    def test_office_list_and_detail(self, authenticated_api_client, office):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:office-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:office-detail", kwargs={"officecode": office.officecode}
            ),
        )

    def test_employee_list_and_detail(self, authenticated_api_client, employee):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:employee-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:employee-detail",
                kwargs={"employeenumber": employee.employeenumber},
            ),
        )

    def test_order_list_and_detail(self, authenticated_api_client, order):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:order-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:order-detail",
                kwargs={"ordernumber": order.ordernumber},
            ),
        )

    def test_payment_list_and_detail(self, authenticated_api_client, payment):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:payment-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:payment-detail",
                kwargs={
                    "customerNumber": payment.customernumber.customernumber,
                    "checkNumber": payment.checknumber,
                },
            ),
        )

    def test_orderdetail_list_and_detail(
        self, authenticated_api_client, order_detail
    ):
        assert_optional_slash(
            authenticated_api_client, reverse("classicmodels:orderdetail-list")
        )
        assert_optional_slash(
            authenticated_api_client,
            reverse(
                "classicmodels:orderdetail-detail",
                kwargs={
                    "orderNumber": order_detail.ordernumber.ordernumber,
                    "productCode": order_detail.productcode.productcode,
                },
            ),
        )

    def test_nested_customer_actions(self, authenticated_api_client, customer):
        base = reverse(
            "classicmodels:customer-detail",
            kwargs={"customernumber": customer.customernumber},
        ).rstrip("/")
        assert_optional_slash(authenticated_api_client, f"{base}/payments/")
        assert_optional_slash(authenticated_api_client, f"{base}/orders/")

    def test_nested_order_action(self, authenticated_api_client, order):
        base = reverse(
            "classicmodels:order-detail",
            kwargs={"ordernumber": order.ordernumber},
        ).rstrip("/")
        assert_optional_slash(authenticated_api_client, f"{base}/order-details/")

    def test_nested_office_employees(self, authenticated_api_client, office):
        base = reverse(
            "classicmodels:office-detail", kwargs={"officecode": office.officecode}
        ).rstrip("/")
        assert_optional_slash(authenticated_api_client, f"{base}/employees/")

    def test_nested_employee_actions(
        self, authenticated_api_client, manager_employee
    ):
        base = reverse(
            "classicmodels:employee-detail",
            kwargs={"employeenumber": manager_employee.employeenumber},
        ).rstrip("/")
        assert_optional_slash(authenticated_api_client, f"{base}/reports/")
        assert_optional_slash(authenticated_api_client, f"{base}/customers/")

    def test_nested_product_line_action(
        self, authenticated_api_client, product_line
    ):
        base = reverse(
            "classicmodels:productline-detail",
            kwargs={"productline": product_line.productline},
        ).rstrip("/")
        assert_optional_slash(authenticated_api_client, f"{base}/products/")

    def test_nested_product_action(self, authenticated_api_client, product):
        base = reverse(
            "classicmodels:product-detail",
            kwargs={"productcode": product.productcode},
        ).rstrip("/")
        assert_optional_slash(authenticated_api_client, f"{base}/order-details/")
