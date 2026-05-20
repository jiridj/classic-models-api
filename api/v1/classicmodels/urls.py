from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomerViewSet,
    EmployeeViewSet,
    OfficeViewSet,
    OrderdetailViewSet,
    OrderViewSet,
    PaymentViewSet,
    ProductLineViewSet,
    ProductViewSet,
)


class OptionalSlashRouter(DefaultRouter):
    """DRF router that accepts URLs with or without a trailing slash."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register(r"productlines", ProductLineViewSet, basename="productline")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"offices", OfficeViewSet, basename="office")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"customers", CustomerViewSet, basename="customer")
router.register(r"orders", OrderViewSet, basename="order")


urlpatterns = [
    path("", include(router.urls)),
    # Composite-key resources
    # Payment endpoints - composite key: (customerNumber, checkNumber)
    re_path(
        r"^payments/(?P<customerNumber>\d+)/(?P<checkNumber>[^/]+)/?$",
        PaymentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="payment-detail",
    ),
    re_path(
        r"^payments/?$",
        PaymentViewSet.as_view({"get": "list", "post": "create"}),
        name="payment-list",
    ),
    # Order details endpoints - composite key: (orderNumber, productCode)
    # Note: To get all items for an order, use GET /orders/{ordernumber}/order-details/
    re_path(
        r"^orderdetails/(?P<orderNumber>\d+)/(?P<productCode>[^/]+)/?$",
        OrderdetailViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="orderdetail-detail",
    ),
    re_path(
        r"^orderdetails/?$",
        OrderdetailViewSet.as_view({"get": "list", "post": "create"}),
        name="orderdetail-list",
    ),
]
