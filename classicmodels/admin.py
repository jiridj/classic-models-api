from django.contrib import admin

from . import models


@admin.register(models.ProductLine)
class ProductLineAdmin(admin.ModelAdmin):
    list_display = ("productline",)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("productcode", "productname", "productline", "quantityinstock")
    search_fields = ("productcode", "productname")


@admin.register(models.Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("officecode", "city", "country", "phone")


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employeenumber", "firstname", "lastname", "jobtitle", "officecode")


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customernumber", "customername", "country", "phone")
    search_fields = ("customername", "contactfirstname", "contactlastname")


@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("customernumber", "checknumber", "paymentdate", "amount")


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("ordernumber", "orderdate", "status", "customernumber")
    list_filter = ("status",)


@admin.register(models.Orderdetail)
class OrderdetailAdmin(admin.ModelAdmin):
    list_display = ("ordernumber", "productcode", "quantityordered", "priceeach")
