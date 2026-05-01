from django.urls import include, path
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


# Use standard DRF router with trailing slashes
# Django's APPEND_SLASH setting handles requests without trailing slashes
router = DefaultRouter()
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
    # Order details endpoints - composite key: (orderNumber, productCode)
    # Note: To get all items for an order, use GET /orders/{ordernumber}/order-details/
    path(
        "orderdetails/<int:orderNumber>/<str:productCode>/",
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
    path(
        "orderdetails/",
        OrderdetailViewSet.as_view({"get": "list", "post": "create"}),
        name="orderdetail-list",
    ),
]
