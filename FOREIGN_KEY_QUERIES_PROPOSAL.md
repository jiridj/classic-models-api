# Foreign Key Query Analysis & Proposal

## Executive Summary

Currently, the Classic Models API only supports querying resources by their primary key. This document analyzes the database model's foreign key relationships and proposes useful cross-resource queries that would enhance the API's functionality for common business use cases.

## Database Model Analysis

### Foreign Key Relationships

The database model contains the following foreign key relationships:

1. **Product → ProductLine**
   - Field: `productline` (FK to `ProductLine.productline`)
   - Relationship: Many-to-One (many products belong to one product line)

2. **Employee → Office**
   - Field: `officecode` (FK to `Office.officecode`)
   - Relationship: Many-to-One (many employees work in one office)

3. **Employee → Employee** (Self-referential)
   - Field: `reportsto` (FK to `Employee.employeenumber`)
   - Relationship: Many-to-One (many employees report to one manager)

4. **Customer → Employee**
   - Field: `salesrepemployeenumber` (FK to `Employee.employeenumber`)
   - Relationship: Many-to-One (many customers assigned to one sales rep)

5. **Payment → Customer**
   - Field: `customernumber` (FK to `Customer.customernumber`)
   - Relationship: Many-to-One (many payments from one customer)

6. **Order → Customer**
   - Field: `customernumber` (FK to `Customer.customernumber`)
   - Relationship: Many-to-One (many orders from one customer)

7. **Orderdetail → Order**
   - Field: `ordernumber` (FK to `Order.ordernumber`)
   - Relationship: Many-to-One (many line items in one order)

8. **Orderdetail → Product**
   - Field: `productcode` (FK to `Product.productcode`)
   - Relationship: Many-to-One (many order details for one product)

## Proposed Queries

### Priority 1: High-Value Business Queries

These queries directly address the use cases mentioned and are likely to be frequently used:

#### 1. Customer Sales History
**Endpoint:** `GET /api/v1/customers/{customerNumber}/orders/`
- **Description:** Get all orders for a specific customer
- **Use Case:** "Give me all sales history for customer XYZ"
- **Implementation:** Filter `Order` by `customernumber`
- **Response:** List of orders with order details optionally included

**Alternative:** `GET /api/v1/customers/{customerNumber}/order-details/`
- **Description:** Get all order details (line items) for a customer
- **Use Case:** Complete purchase history including products
- **Implementation:** Filter `Orderdetail` via `Order` by `customernumber`

#### 2. Customer Payment History
**Endpoint:** `GET /api/v1/customers/{customerNumber}/payments/`
- **Description:** Get all payments made by a specific customer
- **Use Case:** Payment tracking and financial reconciliation
- **Implementation:** Filter `Payment` by `customernumber`

#### 3. Top Selling Products
**Endpoint:** `GET /api/v1/products/top-selling/?limit=5`
- **Description:** Get top N best-selling products by quantity or revenue
- **Use Case:** "What are my top 5 best-selling products"
- **Implementation:** Aggregate `Orderdetail` by `productcode`, sum `quantityordered` or `quantityordered * priceeach`
- **Query Parameters:**
  - `limit`: Number of top products to return (default: 10)
  - `order_by`: `quantity` or `revenue` (default: `quantity`)
  - `date_from`: Optional start date filter
  - `date_to`: Optional end date filter

#### 4. Product Order History
**Endpoint:** `GET /api/v1/products/{productCode}/order-details/`
- **Description:** Get all order details (sales) for a specific product
- **Use Case:** Product sales analysis and inventory planning
- **Implementation:** Filter `Orderdetail` by `productcode`

### Priority 2: Organizational & Relationship Queries

These queries support organizational structure and relationship navigation:

#### 5. Products by Product Line
**Endpoint:** `GET /api/v1/productlines/{productLine}/products/`
- **Description:** Get all products in a specific product line
- **Use Case:** Browse products by category
- **Implementation:** Filter `Product` by `productline`

#### 6. Employees by Office
**Endpoint:** `GET /api/v1/offices/{officeCode}/employees/`
- **Description:** Get all employees working in a specific office
- **Use Case:** Office management and organizational charts
- **Implementation:** Filter `Employee` by `officecode`

#### 7. Employees by Manager
**Endpoint:** `GET /api/v1/employees/{employeeNumber}/subordinates/`
- **Description:** Get all employees reporting to a specific manager
- **Use Case:** Organizational hierarchy and team management
- **Implementation:** Filter `Employee` by `reportsto`

#### 8. Customers by Sales Rep
**Endpoint:** `GET /api/v1/employees/{employeeNumber}/customers/`
- **Description:** Get all customers assigned to a specific sales representative
- **Use Case:** Sales rep performance tracking and customer management
- **Implementation:** Filter `Customer` by `salesrepemployeenumber`

#### 9. Order Details by Order
**Endpoint:** `GET /api/v1/orders/{orderNumber}/order-details/`
- **Description:** Get all line items for a specific order
- **Use Case:** Order fulfillment and invoice generation
- **Implementation:** Filter `Orderdetail` by `ordernumber`

### Priority 3: Analytics & Aggregation Queries

These queries provide business intelligence and reporting capabilities:

#### 10. Sales by Customer
**Endpoint:** `GET /api/v1/customers/sales-summary/`
- **Description:** Get sales summary (total revenue, order count) per customer
- **Use Case:** Customer value analysis
- **Implementation:** Aggregate `Orderdetail` via `Order` by `customernumber`
- **Query Parameters:**
  - `date_from`: Optional start date filter
  - `date_to`: Optional end date filter
  - `order_by`: `revenue` or `orders` (default: `revenue`)

#### 11. Sales by Sales Rep
**Endpoint:** `GET /api/v1/employees/{employeeNumber}/sales-summary/`
- **Description:** Get sales summary for a specific sales representative
- **Use Case:** Sales performance evaluation
- **Implementation:** Aggregate `Orderdetail` via `Order` → `Customer` by `salesrepemployeenumber`
- **Query Parameters:**
  - `date_from`: Optional start date filter
  - `date_to`: Optional end date filter

#### 12. Products by Order Count
**Endpoint:** `GET /api/v1/products/?order_by=order_count`
- **Description:** List products sorted by number of orders
- **Use Case:** Product popularity analysis
- **Implementation:** Annotate `Product` queryset with order count from `Orderdetail`

## Implementation Recommendations

### URL Structure

Two approaches are recommended:

#### Approach 1: Nested Resources (RESTful)
```
/api/v1/customers/{customerNumber}/orders/
/api/v1/customers/{customerNumber}/payments/
/api/v1/products/{productCode}/order-details/
/api/v1/productlines/{productLine}/products/
/api/v1/offices/{officeCode}/employees/
/api/v1/employees/{employeeNumber}/subordinates/
/api/v1/employees/{employeeNumber}/customers/
/api/v1/orders/{orderNumber}/order-details/
```

**Pros:**
- Clear hierarchical relationship
- RESTful and intuitive
- Easy to understand resource relationships

**Cons:**
- More complex URL routing
- Requires nested viewset configuration

#### Approach 2: Query Parameters (Simpler)
```
/api/v1/orders/?customer={customerNumber}
/api/v1/payments/?customer={customerNumber}
/api/v1/orderdetails/?product={productCode}
/api/v1/products/?productline={productLine}
/api/v1/employees/?office={officeCode}
/api/v1/employees/?reports_to={employeeNumber}
/api/v1/customers/?salesrep={employeeNumber}
/api/v1/orderdetails/?order={orderNumber}
```

**Pros:**
- Simpler implementation
- Consistent with existing list endpoints
- Easy to combine multiple filters

**Cons:**
- Less explicit about relationships
- Can be less intuitive for nested relationships

### Recommended Hybrid Approach

Use **nested resources** for primary relationships (customer orders, customer payments) and **query parameters** for secondary relationships and analytics:

- **Nested:** Customer orders, customer payments, order details by order
- **Query Parameters:** Products by product line, employees by office, top-selling products, sales summaries

### Implementation Details

1. **Filtering:** Use Django REST Framework's `django_filters` or custom filtering backends
2. **Pagination:** All list endpoints should support pagination (already implemented)
3. **Performance:** Use `select_related()` and `prefetch_related()` for efficient queries
4. **Caching:** Consider caching for analytics queries (top-selling products, sales summaries)

### Example Implementation Pattern

For nested resources:
```python
# In urls.py
router.register(r'customers', CustomerViewSet, basename='customer')
# Add nested route
urlpatterns += [
    path('customers/<int:customernumber>/orders/', 
         CustomerOrdersViewSet.as_view({'get': 'list'}), 
         name='customer-orders'),
]

# In views.py
class CustomerOrdersViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        customer_number = self.kwargs['customernumber']
        return Order.objects.filter(customernumber_id=customer_number)
```

For query parameters:
```python
# In views.py
class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_line = self.request.query_params.get('productline')
        if product_line:
            queryset = queryset.filter(productline_id=product_line)
        return queryset
```

## Priority Implementation Order

1. **Phase 1 (Critical):**
   - Customer orders (`/customers/{id}/orders/`)
   - Top selling products (`/products/top-selling/`)
   - Order details by order (`/orders/{id}/order-details/`)

2. **Phase 2 (High Value):**
   - Customer payments (`/customers/{id}/payments/`)
   - Product order history (`/products/{id}/order-details/`)
   - Products by product line (`/productlines/{id}/products/`)

3. **Phase 3 (Organizational):**
   - Employees by office (`/offices/{id}/employees/`)
   - Customers by sales rep (`/employees/{id}/customers/`)
   - Employees by manager (`/employees/{id}/subordinates/`)

4. **Phase 4 (Analytics):**
   - Sales by customer (`/customers/sales-summary/`)
   - Sales by sales rep (`/employees/{id}/sales-summary/`)
   - Products by order count (enhance existing endpoint)

## Testing Considerations

Each new endpoint should have:
- Authentication tests (401 for unauthenticated)
- Authorization tests (if applicable)
- Filtering accuracy tests
- Pagination tests
- Edge case tests (non-existent parent resource, empty results)
- Performance tests for large datasets

## Documentation Updates

Update OpenAPI/Swagger documentation to include:
- New endpoint descriptions
- Query parameter specifications
- Example requests and responses
- Relationship diagrams showing how resources connect

