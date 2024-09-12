from django.contrib import admin
from .models import Product, Expense, Transaction, TransactionProduct

admin.site.register(Product)
admin.site.register(Expense)
admin.site.register(Transaction)
admin.site.register(TransactionProduct)
