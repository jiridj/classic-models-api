from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter

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
    """Router that accepts URLs with or without trailing slashes."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trailing_slash = '/?'


# Configure router to work with or without trailing slashes
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
    # Payment detail (with trailing slash)
    path(
        "payments/<int:customerNumber>/<str:checkNumber>/",
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
    # Payment detail (without trailing slash)
    path(
        "payments/<int:customerNumber>/<str:checkNumber>",
        PaymentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    # Payment list (with trailing slash)
    path(
        "payments/",
        PaymentViewSet.as_view({"get": "list", "post": "create"}),
        name="payment-list",
    ),
    # Payment list (without trailing slash)
    path(
        "payments",
        PaymentViewSet.as_view({"get": "list", "post": "create"}),
    ),
    # Order details by order number (with trailing slash)
    path(
        "orderdetails/<int:orderNumber>/",
        OrderdetailViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
        name="orderdetail-detail",
    ),
    # Order details by order number (without trailing slash)
    path(
        "orderdetails/<int:orderNumber>",
        OrderdetailViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
    ),
    # Order detail item operations (with trailing slash)
    path(
        "orderdetails/<int:orderNumber>/<str:productCode>/",
        OrderdetailViewSet.as_view(
            {
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="orderdetail-item-detail",
    ),
    # Order detail item operations (without trailing slash)
    path(
        "orderdetails/<int:orderNumber>/<str:productCode>",
        OrderdetailViewSet.as_view(
            {
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
    ),
    # Order details list (with trailing slash)
    path(
        "orderdetails/",
        OrderdetailViewSet.as_view({"get": "list", "post": "create"}),
        name="orderdetail-list",
    ),
    # Order details list (without trailing slash)
    path(
        "orderdetails",
        OrderdetailViewSet.as_view({"get": "list", "post": "create"}),
    ),
]
