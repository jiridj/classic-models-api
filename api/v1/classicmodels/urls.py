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
    # Payment endpoints - trailing slash in spec, accepts with or without via APPEND_SLASH
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
    path(
        "payments/",
        PaymentViewSet.as_view({"get": "list", "post": "create"}),
        name="payment-list",
    ),
    # Order details endpoints - trailing slash in spec, accepts with or without via APPEND_SLASH
    path(
        "orderdetails/<int:orderNumber>/",
        OrderdetailViewSet.as_view(
            {
                "get": "retrieve",
            }
        ),
        name="orderdetail-detail",
    ),
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
    path(
        "orderdetails/",
        OrderdetailViewSet.as_view({"get": "list", "post": "create"}),
        name="orderdetail-list",
    ),
]
