
from django.urls import path
from .views import (
    ProductList, ProductDelete, ProductCreate, ProductUpdate,
    ExpenseList, ExpenseDelete, ExpenseCreate, ExpenseUpdate,
    TransactionList, TransactionDelete, TransactionCreate, TransactionUpdate,
)

urlpatterns = [
    # Product URLs
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/create/', ProductCreate.as_view(), name='product-create'),
    path('products/delete/<int:pk>/',
         ProductDelete.as_view(), name='product-delete'),
    path('products/update/<int:pk>/',
         ProductUpdate.as_view(), name='product-update'),

    # Expense URLs
    path('expenses/', ExpenseList.as_view(), name='expense-list'),
    path('expenses/create/', ExpenseCreate.as_view(), name='expense-create'),
    path('expenses/delete/<int:pk>/',
         ExpenseDelete.as_view(), name='expense-delete'),
    path('products/update/<int:pk>/',
         ExpenseUpdate.as_view(), name='expense-update'),

    # Transaction URLs
    path('transactions/', TransactionList.as_view(), name='transaction-list'),
    path('transactions/create/', TransactionCreate.as_view(),
         name='transaction-create'),
    path('transactions/delete/<int:pk>/',
         TransactionDelete.as_view(), name='transaction-delete'),
    path('transactions/update/<int:pk>/',
         TransactionUpdate.as_view(), name='transaction-update'),
]
