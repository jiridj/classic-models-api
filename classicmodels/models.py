from django.db import models


class ProductLine(models.Model):
    productline = models.CharField(db_column="productLine", primary_key=True, max_length=50)
    textdescription = models.CharField(db_column="textDescription", max_length=4000, blank=True, null=True)
    htmldescription = models.TextField(db_column="htmlDescription", blank=True, null=True)
    image = models.BinaryField(blank=True, null=True)

    def __str__(self):
        return self.productline

    class Meta:
        managed = False
        db_table = "productlines"


class Product(models.Model):
    productcode = models.CharField(db_column="productCode", primary_key=True, max_length=15)
    productname = models.CharField(db_column="productName", max_length=70)
    productline = models.ForeignKey(ProductLine, models.DO_NOTHING, db_column="productLine")
    productscale = models.CharField(db_column="productScale", max_length=10)
    productvendor = models.CharField(db_column="productVendor", max_length=50)
    productdescription = models.TextField(db_column="productDescription")
    quantityinstock = models.SmallIntegerField(db_column="quantityInStock")
    buyprice = models.DecimalField(db_column="buyPrice", max_digits=10, decimal_places=2)
    msrp = models.DecimalField(db_column="MSRP", max_digits=10, decimal_places=2)

    def __str__(self):
        return self.productcode

    class Meta:
        managed = False
        db_table = "products"


class Office(models.Model):
    officecode = models.CharField(db_column="officeCode", primary_key=True, max_length=10)
    city = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    addressline1 = models.CharField(db_column="addressLine1", max_length=50)
    addressline2 = models.CharField(db_column="addressLine2", max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50)
    postalcode = models.CharField(db_column="postalCode", max_length=15)
    territory = models.CharField(max_length=10)

    def __str__(self):
        return self.officecode

    class Meta:
        managed = False
        db_table = "offices"


class Employee(models.Model):
    employeenumber = models.IntegerField(db_column="employeeNumber", primary_key=True)
    lastname = models.CharField(db_column="lastName", max_length=50)
    firstname = models.CharField(db_column="firstName", max_length=50)
    extension = models.CharField(max_length=10)
    email = models.CharField(max_length=100)
    officecode = models.ForeignKey(Office, models.DO_NOTHING, db_column="officeCode")
    reportsto = models.ForeignKey(
        "self", models.DO_NOTHING, db_column="reportsTo", blank=True, null=True, to_field="employeenumber"
    )
    jobtitle = models.CharField(db_column="jobTitle", max_length=50)

    def __str__(self):
        return str(self.employeenumber)

    class Meta:
        managed = False
        db_table = "employees"


class Customer(models.Model):
    customernumber = models.IntegerField(db_column="customerNumber", primary_key=True)
    customername = models.CharField(db_column="customerName", max_length=50)
    contactlastname = models.CharField(db_column="contactLastName", max_length=50)
    contactfirstname = models.CharField(db_column="contactFirstName", max_length=50)
    phone = models.CharField(max_length=50)
    addressline1 = models.CharField(db_column="addressLine1", max_length=50)
    addressline2 = models.CharField(db_column="addressLine2", max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, blank=True, null=True)
    postalcode = models.CharField(db_column="postalCode", max_length=15, blank=True, null=True)
    country = models.CharField(max_length=50)
    salesrepemployeenumber = models.ForeignKey(
        Employee, models.DO_NOTHING, db_column="salesRepEmployeeNumber", blank=True, null=True, to_field="employeenumber"
    )
    creditlimit = models.DecimalField(db_column="creditLimit", max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return str(self.customernumber)

    class Meta:
        managed = False
        db_table = "customers"


class Payment(models.Model):
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column="customerNumber", to_field="customernumber")
    checknumber = models.CharField(db_column="checkNumber", max_length=50)
    paymentdate = models.DateField(db_column="paymentDate")
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customernumber}-{self.checknumber}"

    class Meta:
        managed = False
        db_table = "payments"
        unique_together = (("customernumber", "checknumber"),)


class Order(models.Model):
    ordernumber = models.IntegerField(db_column="orderNumber", primary_key=True)
    orderdate = models.DateField(db_column="orderDate")
    requireddate = models.DateField(db_column="requiredDate")
    shippeddate = models.DateField(db_column="shippedDate", blank=True, null=True)
    status = models.CharField(max_length=15)
    comments = models.TextField(blank=True, null=True)
    customernumber = models.ForeignKey(Customer, models.DO_NOTHING, db_column="customerNumber", to_field="customernumber")

    def __str__(self):
        return str(self.ordernumber)

    class Meta:
        managed = False
        db_table = "orders"


class Orderdetail(models.Model):
    ordernumber = models.ForeignKey(Order, models.DO_NOTHING, db_column="orderNumber", to_field="ordernumber")
    productcode = models.ForeignKey(Product, models.DO_NOTHING, db_column="productCode", to_field="productcode")
    quantityordered = models.IntegerField(db_column="quantityOrdered")
    priceeach = models.DecimalField(db_column="priceEach", max_digits=10, decimal_places=2)
    orderlinenumber = models.SmallIntegerField(db_column="orderLineNumber")

    def __str__(self):
        return f"{self.ordernumber}-{self.productcode}"

    class Meta:
        managed = False
        db_table = "orderdetails"
        unique_together = ("ordernumber", "productcode")


