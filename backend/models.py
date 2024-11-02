from django.db import models


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=100, default="MyProduct")
    stock = models.IntegerField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2)
    number_sold = models.IntegerField(default=0)
    is_retired = models.BooleanField(default=False)


class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date = models.DateField()
    type = models.CharField(max_length=50)
    price = models.DecimalField(
        max_digits=10, decimal_places=2)


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    type = models.CharField(max_length=50)
    products = models.TextField()


class TransactionProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
