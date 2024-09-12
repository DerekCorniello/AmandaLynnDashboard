from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from .models import Product, Expense, Transaction
import json


def apply_sorting_and_filtering(queryset, request, allowed_sort_fields):
    filters = {key: value for key, value in request.GET.items() if key not in [
        'sort_by', 'order', 'search']}
    queryset = queryset.filter(**filters)

    # Apply search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        search_conditions = Q()  # An empty Q object for OR conditions
        for field in allowed_sort_fields:
            search_conditions |= Q(**{f'{field}__icontains': search_query})
        queryset = queryset.filter(search_conditions)

    # Apply sorting
    sort_by = request.GET.get('sort_by')
    order = request.GET.get('order', 'asc')

    if sort_by in allowed_sort_fields:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        queryset = queryset.order_by(sort_by)

    return queryset


class ProductList(View):
    def get(self, request):
        products = Product.objects.all()
        allowed_sort_fields = ['name', 'price', 'stock', 'number_sold']
        products = apply_sorting_and_filtering(
            products, request, allowed_sort_fields)
        products = list(products.values())
        return JsonResponse(products, safe=False)


class ProductDelete(View):
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)


class ProductCreate(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            valid_products = Product.objects.values_list('name', flat=True)
            if data['name'] in valid_products:
                return JsonResponse({'error': f'Product already exists: {data['name']}'}, status=400)

            product = Product.objects.create(
                name=data['name'],
                stock=data['stock'],
                price=data['price'],
                number_sold=data['number_sold']
            )
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'stock': product.stock,
                'price': product.price,
                'number_sold': product.number_sold
            }, status=201)
        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


class ProductUpdate(View):
    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            product = Product.objects.get(pk=pk)
            valid_products = Product.objects.values_list('name', flat=True)
            if data['name'] in valid_products and data['name'] != product.name:
                return JsonResponse({'error': f'Product already exists: {data['name']}'}, status=400)

            for field in ['name', 'stock', 'price', 'number_sold']:
                if field in data:
                    setattr(product, field, data[field])

            product.save()
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'stock': product.stock,
                'price': product.price,
                'number_sold': product.number_sold
            })
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


class ExpenseList(View):
    def get(self, request):
        expenses = Expense.objects.all()
        allowed_sort_fields = ['name', 'date', 'price', 'type']
        expenses = apply_sorting_and_filtering(
            expenses, request, allowed_sort_fields)
        expenses = list(expenses.values())
        return JsonResponse(expenses, safe=False)


class ExpenseDelete(View):
    def delete(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)
            expense.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except Expense.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)


class ExpenseCreate(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            expense = Expense.objects.create(
                name=data['name'],
                date=data['date'],
                type=data['type'],
                price=data['price']
            )
            return JsonResponse({
                'id': expense.id,
                'name': expense.name,
                'date': expense.date,
                'type': expense.type,
                'price': expense.price
            }, status=201)
        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


class ExpenseUpdate(View):
    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            expense = Expense.objects.get(pk=pk)

            for field in ['name', 'date', 'type', 'price']:
                if field in data:
                    setattr(expense, field, data[field])

            expense.save()
            return JsonResponse({
                'date': expense.date,
                'name': expense.name,
                'type': expense.type,
                'price': expense.price,
            })
        except Expense.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


class TransactionList(View):
    def get(self, request):
        transactions = Transaction.objects.all()
        allowed_sort_fields = ['date', 'total', 'type']
        transactions = apply_sorting_and_filtering(
            transactions, request, allowed_sort_fields)

        transaction_data = []
        for transaction in transactions:

            product_names = transaction.products

            transaction_data.append({
                'id': transaction.id,
                'total': transaction.total,
                'date': transaction.date,
                'type': transaction.type,
                'products': product_names
            })

        return JsonResponse(transaction_data, safe=False)


class TransactionDelete(View):
    def delete(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk)
            transaction.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)


class TransactionCreate(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            product_names_str = data.get('products', '')

            product_names_list = [product.strip()
                                  for product in product_names_str.split(',')]

            valid_products = Product.objects.values_list('name', flat=True)

            for product in product_names_list:
                if product not in valid_products:
                    return JsonResponse({'error': f'Product does not exist: {product}'}, status=400)

            transaction = Transaction.objects.create(
                total=data['total'],
                date=data['date'],
                type=data['type']
            )

            transaction.products = product_names_str
            transaction.save()

            return JsonResponse({
                'id': transaction.id,
                'total': transaction.total,
                'date': transaction.date,
                'type': transaction.type,
                'products': product_names_str
            }, status=201)

        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)


class TransactionUpdate(View):
    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            transaction = Transaction.objects.get(pk=pk)

            for field in ['total', 'date', 'type']:
                if field in data:
                    setattr(transaction, field, data[field])

            product_names_str = data.get('products', '')

            product_names_list = [product.strip()
                                  for product in product_names_str.split(',')]

            valid_products = Product.objects.values_list('name', flat=True)

            for product in product_names_list:
                if product not in valid_products:
                    return JsonResponse({'error': f'Product does not exist: {product}'}, status=400)

            transaction.products = product_names_str
            transaction.save()

            return JsonResponse({
                'id': transaction.id,
                'total': transaction.total,
                'date': transaction.date,
                'type': transaction.type,
                'products': product_names_str
            })

        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
