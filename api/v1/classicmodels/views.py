from rest_framework import mixins, viewsets, status, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view

from classicmodels.models import (
    Customer,
    Employee,
    Office,
    Order,
    Orderdetail,
    Payment,
    Product,
    ProductLine,
)
from .serializers import (
    CustomerSerializer,
    EmployeeSerializer,
    OfficeSerializer,
    OrderSerializer,
    OrderdetailSerializer,
    PaymentSerializer,
    ProductLineSerializer,
    ProductSerializer,
)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
        operation_id="list_product_lines", 
        tags=["Product Lines"],
        summary="List all product lines",
        description="Retrieve a paginated list of all product line categories in the system.",
    ),
    create=extend_schema(
        operation_id="create_product_line", 
        tags=["Product Lines"],
        summary="Create a new product line",
        description="Add a new product line category to the system."
    ),
    retrieve=extend_schema(
        operation_id="get_product_line", 
        tags=["Product Lines"],
        summary="Get a specific product line",
        description="Retrieve detailed information about a specific product line by its identifier."
    ),
    update=extend_schema(
        operation_id="update_product_line", 
        tags=["Product Lines"],
        summary="Update a product line",
        description="Update all fields of an existing product line."
    ),
    partial_update=extend_schema(
        operation_id="patch_product_line", 
        tags=["Product Lines"],
        summary="Partially update a product line",
        description="Update specific fields of an existing product line."
    ),
    destroy=extend_schema(
        operation_id="delete_product_line", 
        tags=["Product Lines"],
        summary="Delete a product line",
        description="Remove a product line from the system."
    ),
)
class ProductLineViewSet(BaseModelViewSet):
    queryset = ProductLine.objects.all()
    serializer_class = ProductLineSerializer
    lookup_field = "productline"


@extend_schema_view(
    list=extend_schema(
        operation_id="list_products", 
        tags=["Products"],
        summary="List all products",
        description="Retrieve a paginated list of all products in the catalog with their details."
    ),
    create=extend_schema(
        operation_id="create_product", 
        tags=["Products"],
        summary="Create a new product",
        description="Add a new product to the catalog with all required information."
    ),
    retrieve=extend_schema(
        operation_id="get_product", 
        tags=["Products"],
        summary="Get a specific product",
        description="Retrieve detailed information about a specific product by its code."
    ),
    update=extend_schema(
        operation_id="update_product", 
        tags=["Products"],
        summary="Update a product",
        description="Update all fields of an existing product in the catalog."
    ),
    partial_update=extend_schema(
        operation_id="patch_product", 
        tags=["Products"],
        summary="Partially update a product",
        description="Update specific fields of an existing product."
    ),
    destroy=extend_schema(
        operation_id="delete_product", 
        tags=["Products"],
        summary="Delete a product",
        description="Remove a product from the catalog."
    ),
)
class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = "productcode"


@extend_schema_view(
    list=extend_schema(
        operation_id="list_offices", 
        tags=["Offices"],
        summary="List all offices",
        description="Retrieve a paginated list of all company office locations worldwide."
    ),
    create=extend_schema(
        operation_id="create_office", 
        tags=["Offices"],
        summary="Create a new office",
        description="Add a new office location to the company's network."
    ),
    retrieve=extend_schema(
        operation_id="get_office", 
        tags=["Offices"],
        summary="Get a specific office",
        description="Retrieve detailed information about a specific office by its code."
    ),
    update=extend_schema(
        operation_id="update_office", 
        tags=["Offices"],
        summary="Update an office",
        description="Update all fields of an existing office location."
    ),
    partial_update=extend_schema(
        operation_id="patch_office", 
        tags=["Offices"],
        summary="Partially update an office",
        description="Update specific fields of an existing office location."
    ),
    destroy=extend_schema(
        operation_id="delete_office", 
        tags=["Offices"],
        summary="Delete an office",
        description="Remove an office location from the company network."
    ),
)
class OfficeViewSet(BaseModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    lookup_field = "officecode"


@extend_schema_view(
    list=extend_schema(
        operation_id="list_employees", 
        tags=["Employees"],
        summary="List all employees",
        description="Retrieve a paginated list of all employees in the organization with their details."
    ),
    create=extend_schema(
        operation_id="create_employee", 
        tags=["Employees"],
        summary="Create a new employee",
        description="Add a new employee to the organization with their job details and office assignment."
    ),
    retrieve=extend_schema(
        operation_id="get_employee", 
        tags=["Employees"],
        summary="Get a specific employee",
        description="Retrieve detailed information about a specific employee by their employee number."
    ),
    update=extend_schema(
        operation_id="update_employee", 
        tags=["Employees"],
        summary="Update an employee",
        description="Update all fields of an existing employee record."
    ),
    partial_update=extend_schema(
        operation_id="patch_employee", 
        tags=["Employees"],
        summary="Partially update an employee",
        description="Update specific fields of an existing employee record."
    ),
    destroy=extend_schema(
        operation_id="delete_employee", 
        tags=["Employees"],
        summary="Delete an employee",
        description="Remove an employee from the organization."
    ),
)
class EmployeeViewSet(BaseModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "employeenumber"


@extend_schema_view(
    list=extend_schema(
        operation_id="list_customers", 
        tags=["Customers"],
        summary="List all customers",
        description="Retrieve a paginated list of all customers with their contact and credit information."
    ),
    create=extend_schema(
        operation_id="create_customer", 
        tags=["Customers"],
        summary="Create a new customer",
        description="Add a new customer to the system with their contact details and credit limit."
    ),
    retrieve=extend_schema(
        operation_id="get_customer", 
        tags=["Customers"],
        summary="Get a specific customer",
        description="Retrieve detailed information about a specific customer by their customer number."
    ),
    update=extend_schema(
        operation_id="update_customer", 
        tags=["Customers"],
        summary="Update a customer",
        description="Update all fields of an existing customer record."
    ),
    partial_update=extend_schema(
        operation_id="patch_customer", 
        tags=["Customers"],
        summary="Partially update a customer",
        description="Update specific fields of an existing customer record."
    ),
    destroy=extend_schema(
        operation_id="delete_customer", 
        tags=["Customers"],
        summary="Delete a customer",
        description="Remove a customer from the system."
    ),
)
class CustomerViewSet(BaseModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = "customernumber"


@extend_schema_view(
    list=extend_schema(
        operation_id="list_orders", 
        tags=["Orders"],
        summary="List all orders",
        description="Retrieve a paginated list of all customer orders with their status and details."
    ),
    create=extend_schema(
        operation_id="create_order", 
        tags=["Orders"],
        summary="Create a new order",
        description="Create a new customer order with order date, required date, and status information."
    ),
    retrieve=extend_schema(
        operation_id="get_order", 
        tags=["Orders"],
        summary="Get a specific order",
        description="Retrieve detailed information about a specific order by its order number."
    ),
    update=extend_schema(
        operation_id="update_order", 
        tags=["Orders"],
        summary="Update an order",
        description="Update all fields of an existing order record."
    ),
    partial_update=extend_schema(
        operation_id="patch_order", 
        tags=["Orders"],
        summary="Partially update an order",
        description="Update specific fields of an existing order record."
    ),
    destroy=extend_schema(
        operation_id="delete_order", 
        tags=["Orders"],
        summary="Delete an order",
        description="Remove an order from the system."
    ),
)
class OrderViewSet(BaseModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "ordernumber"


@extend_schema_view(
    list=extend_schema(
        operation_id="list_payments", 
        tags=["Payments"],
        summary="List all payments",
        description="Retrieve a paginated list of all customer payment records with amounts and dates."
    ),
    create=extend_schema(
        operation_id="create_payment", 
        tags=["Payments"],
        summary="Create a new payment",
        description="Record a new customer payment with check number, amount, and payment date."
    ),
    retrieve=extend_schema(
        operation_id="get_payment", 
        tags=["Payments"],
        summary="Get a specific payment",
        description="Retrieve detailed information about a specific payment by customer number and check number."
    ),
    update=extend_schema(
        operation_id="update_payment", 
        tags=["Payments"],
        summary="Update a payment",
        description="Update all fields of an existing payment record."
    ),
    partial_update=extend_schema(
        operation_id="patch_payment", 
        tags=["Payments"],
        summary="Partially update a payment",
        description="Update specific fields of an existing payment record."
    ),
    destroy=extend_schema(
        operation_id="delete_payment", 
        tags=["Payments"],
        summary="Delete a payment",
        description="Remove a payment record from the system."
    ),
)
class PaymentViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    queryset = Payment.objects.select_related("customernumber")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        customer_number = self.kwargs.get("customerNumber")
        check_number = self.kwargs.get("checkNumber")
        return get_object_or_404(
            Payment, customernumber_id=customer_number, checknumber=check_number
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        operation_id="list_order_details", 
        tags=["Order Details"],
        summary="List all order details",
        description="Retrieve a paginated list of all order line items with product and quantity information."
    ),
    create=extend_schema(
        operation_id="create_order_detail", 
        tags=["Order Details"],
        summary="Create a new order detail",
        description="Add a new line item to an existing order with product code, quantity, and price."
    ),
    retrieve=extend_schema(
        operation_id="get_order_detail", 
        tags=["Order Details"],
        summary="Get a specific order detail",
        description="Retrieve detailed information about a specific order line item by order number and product code."
    ),
    update=extend_schema(
        operation_id="update_order_detail", 
        tags=["Order Details"],
        summary="Update an order detail",
        description="Update all fields of an existing order line item."
    ),
    partial_update=extend_schema(
        operation_id="patch_order_detail", 
        tags=["Order Details"],
        summary="Partially update an order detail",
        description="Update specific fields of an existing order line item."
    ),
    destroy=extend_schema(
        operation_id="delete_order_detail", 
        tags=["Order Details"],
        summary="Delete an order detail",
        description="Remove a line item from an order."
    ),
)
class OrderdetailViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    queryset = Orderdetail.objects.select_related("ordernumber", "productcode")
    serializer_class = OrderdetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        order_number = self.kwargs.get("orderNumber")
        product_code = self.kwargs.get("productCode")
        return get_object_or_404(
            Orderdetail, ordernumber_id=order_number, productcode_id=product_code
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


