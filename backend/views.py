from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.db.models import Q, Sum
from django.db.models.functions import TruncDate
from .models import Product, Expense, Transaction
from collections import defaultdict
from datetime import datetime
import json


def apply_sorting_and_filtering(queryset, request, allowed_sort_fields):
    filters = {key: value for key, value in request.GET.items() if key not in [
        'sort_by', 'order', 'search', 'show_retired']}

    # Apply filters from the request
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


class GraphData(View):

    def _get_money_data(self, timescale):
        today = datetime.now()
        match timescale:
            case 'week':
                start_date = today - datetime.timedelta(days=7)
            case 'month':
                start_date = today - datetime.timedelta(days=30)
            case '3month':
                start_date = today - datetime.timedelta(days=90)
            case '6month':
                start_date = today - datetime.timedelta(days=180)
            case 'year':
                start_date = today - datetime.timedelta(days=365)
            case 'all':
                start_date = datetime.min
            case _:
                return JsonResponse(
                    {'error': 'Invalid time scale'},
                    status=400)

        # Fetch data from Expense model and group by date
        expenses_query = (
            Expense.objects
            .filter(date__gte=start_date)
            .annotate(date=TruncDate('date'))
            .values('date')
            .annotate(total_expense=Sum('price'))
            .values('date', 'total_expense')
        )

        expenses = list(expenses_query)

        # Fetch data from Transaction model and group by date
        transactions_query = (
            Transaction.objects
            .filter(date__gte=start_date)
            .annotate(date=TruncDate('date'))
            .values('date')
            .annotate(total_income=Sum('total'))
            .values('date', 'total_income')
        )

        transactions = list(transactions_query)

        # Aggregate daily data into dictionaries
        daily_expenses = defaultdict(float)
        daily_income = defaultdict(float)

        for expense in expenses:
            daily_expenses[expense['date']] = expense['total_expense']

        for transaction in transactions:
            daily_income[transaction['date']] = transaction['total_income']

        # Prepare data for chart
        dates = sorted(
            set(daily_expenses.keys()).union(daily_income.keys()))
        expense_data = [daily_expenses.get(date, 0) for date in dates]
        income_data = [daily_income.get(date, 0) for date in dates]
        revenue_data = [income - expense for income,
                        expense in zip(income_data, expense_data)]

        return {
            'labels': dates,
            'datasets': [
                {
                    'label': 'Total Income',
                    'data': income_data,
                    'borderColor': '#42A5F5',
                    'backgroundColor': 'rgba(66, 165, 245, 0.2)'
                },
                {
                    'label': 'Total Spending',
                    'data': expense_data,
                    'borderColor': '#66BB6A',
                    'backgroundColor': 'rgba(102, 187, 106, 0.2)'
                },
                {
                    'label': 'Revenue',
                    'data': revenue_data,
                    'borderColor': '#FF7043',
                    'backgroundColor': 'rgba(255, 112, 67, 0.2)'
                }
            ]
        }

    def _get_product_data(self, timescale):
        return

    def _get_timeseries_data(self, request_data):
        try:
            years_str = request_data.get('years', str(datetime.now().year))
            metrics_str = request_data.get('metrics', 'revenue,profit')
            products_str = request_data.get('products', 'all')

            years = [int(y.strip()) for y in years_str.split(',')]
            metrics = [m.strip().lower() for m in metrics_str.split(',')]
            products = [p.strip() for p in products_str.split(',')] if products_str.lower() != 'all' else None

            all_datasets = []
            all_labels = []

            colors = ['#42A5F5', '#FF6384', '#4BC0C0', '#FFCE56', '#36A2EB', '#9966FF', '#FF9F40']

            year_colors = {}
            for i, year in enumerate(years):
                year_colors[year] = colors[i % len(colors)]

            for year in years:
                year_start = datetime(year, 1, 1)
                year_end = datetime(year, 12, 31)

                month_labels = [f'{year}-{str(m).zfill(2)}' for m in range(1, 13)]

                revenue_by_month = defaultdict(float)
                loss_by_month = defaultdict(float)

                transactions = Transaction.objects.filter(date__range=(year_start, year_end))
                expenses = Expense.objects.filter(date__range=(year_start, year_end))

                for transaction in transactions:
                    month = transaction.date.month
                    revenue_by_month[month] += float(transaction.total)

                for expense in expenses:
                    month = expense.date.month
                    loss_by_month[month] += float(expense.price)

                if 'revenue' in metrics:
                    all_datasets.append({
                        'label': f'Revenue {year}',
                        'data': [revenue_by_month[m] for m in range(1, 13)],
                        'borderColor': year_colors[year],
                        'backgroundColor': 'transparent',
                        'borderWidth': 2,
                        'pointRadius': 4,
                        'fill': False
                    })

                if 'loss' in metrics:
                    all_datasets.append({
                        'label': f'Loss {year}',
                        'data': [loss_by_month[m] for m in range(1, 13)],
                        'borderColor': year_colors[year],
                        'backgroundColor': 'transparent',
                        'borderWidth': 2,
                        'pointRadius': 4,
                        'fill': False
                    })

                if 'profit' in metrics:
                    all_datasets.append({
                        'label': f'Profit {year}',
                        'data': [revenue_by_month[m] - loss_by_month[m] for m in range(1, 13)],
                        'borderColor': year_colors[year],
                        'backgroundColor': 'transparent',
                        'borderWidth': 2,
                        'pointRadius': 4,
                        'fill': False
                    })

                all_labels.extend(month_labels)

            if 'product_sales' in metrics:
                selected_products = products
                if not selected_products:
                    all_products = Product.objects.filter(is_retired=False)
                    selected_products = [p.name for p in all_products]

                for year in years:
                    year_start = datetime(year, 1, 1)
                    year_end = datetime(year, 12, 31)

                    product_sales = {}
                    for product in selected_products:
                        product_sales[product] = defaultdict(int)

                    transactions = Transaction.objects.filter(date__range=(year_start, year_end))

                    for transaction in transactions:
                        if isinstance(transaction.products, str):
                            products_list = [p.strip().strip("[]'") for p in transaction.products.split(',')]
                        else:
                            products_list = list(transaction.products)

                        for product_name in products_list:
                            if product_name in product_sales:
                                product_sales[product_name][transaction.date.month] += 1

                    month_labels = [f'{year}-{str(m).zfill(2)}' for m in range(1, 13)]

                    for i, product_name in enumerate(selected_products):
                        all_labels.extend(month_labels)
                        color = colors[(i + len(years)) % len(colors)]
                        all_datasets.append({
                            'label': f'{product_name} Sales {year}',
                            'data': [product_sales[product_name][m] for m in range(1, 13)],
                            'borderColor': color,
                            'backgroundColor': 'transparent',
                            'borderWidth': 2,
                            'pointRadius': 4,
                            'fill': False
                        })

            if not all_datasets:
                return {
                    'labels': [],
                    'datasets': []
                }

            return {
                'labels': list(dict.fromkeys(all_labels)),
                'datasets': all_datasets
            }

        except Exception as e:
            print(f'Error in _get_timeseries_data: {e}')
            return {
                'labels': [],
                'datasets': []
            }

    def post(self, request):
        try:
            data = json.loads(request.body)
            if data['graph'] == 'money':
                res = self._get_money_data(data['timescale'])
            elif data['graph'] == 'product':
                res = self._get_product_data(data['timescale'])
            elif data['graph'] == 'timeseries':
                res = self._get_timeseries_data(data)
            else:
                res = None
                raise KeyError
            return JsonResponse(res, safe=False)
        except KeyError as e:
            return JsonResponse({'error': f'Graph requested `{data["graph"]}` is not available: {e}'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class Status(View):
    def get(self, request):
        try:
            connection.ensure_connection()
            return JsonResponse({"status": "ok"}, status=200)
        except Exception:
            return JsonResponse({"status": "error"}, status=500)


class ProductList(View):
    def get(self, request):
        try:
            show_retired = request.GET.get(
                "show_retired", "false").lower() == "true"
            products = Product.objects.all()

            if not show_retired:
                products = products.filter(is_retired=False)

            allowed_sort_fields = ['name', 'price', 'stock', 'number_sold']
            products = apply_sorting_and_filtering(
                products, request, allowed_sort_fields)

            products = list(products.values())
            return JsonResponse(products, safe=False)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error: {e}'}, status=500)


class ProductDelete(View):
    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class ProductCreate(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            valid_products = Product.objects.values_list('name', flat=True)
            if data['name'].lower() in [p.lower() for p in valid_products]:
                return JsonResponse({'error': f'Product already exists: {data["name"]}'}, status=400)
            if data['name'].lower() == 'unknown':
                return JsonResponse({'error': 'Cannot create Unknown Product'}, status=400)

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
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class ProductUpdate(View):
    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            product = Product.objects.get(pk=pk)
            valid_products = Product.objects.values_list('name', flat=True)

            if data['name'].lower() in [p.lower() for p in valid_products] and data['name'].lower() != product.name.lower():
                return JsonResponse({'error': f'Product already exists: {data["name"]}'}, status=400)
            if data['name'].lower() == 'unknown':
                return JsonResponse({'error': 'Cannot create Unknown Product'}, status=400)

            for field in ['name', 'stock', 'price', 'number_sold', 'is_retired']:
                if field in data:
                    setattr(product, field, data[field])

            product.save()
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'stock': product.stock,
                'price': product.price,
                'number_sold': product.number_sold
            }, status=205)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class ExpenseList(View):
    def get(self, request):
        try:
            expenses = Expense.objects.all()
            allowed_sort_fields = ['name', 'date', 'price', 'type']
            expenses = apply_sorting_and_filtering(
                expenses, request, allowed_sort_fields)
            expenses = list(expenses.values())
            return JsonResponse(expenses, safe=False)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class ExpenseDelete(View):
    def delete(self, request, pk):
        try:
            expense = Expense.objects.get(pk=pk)
            expense.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except Expense.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


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
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


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
            }, status=205)
        except Expense.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class TransactionList(View):
    def get(self, request):
        try:
            transactions = Transaction.objects.all()
            allowed_sort_fields = ['date', 'total', 'type']
            transactions = apply_sorting_and_filtering(
                transactions, request, allowed_sort_fields)

            transaction_data = []
            for transaction in transactions:
                # if this is a string, we do not want to use the comma join
                # or else it will list-ify the string, and list its chars
                if isinstance(transaction.products, str):
                    products = transaction.products
                else:
                    products = ', '.join(transaction.products)
                # trims the '' and [] off of the string
                products = products.replace("'", "")[1:-1]
                transaction_data.append({
                    'id': transaction.id,
                    'total': transaction.total,
                    'date': transaction.date,
                    'type': transaction.type,
                    'products': products
                })

            return JsonResponse(transaction_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class TransactionDelete(View):
    def delete(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk)
            transaction.delete()
            return JsonResponse({'status': 'success'}, status=204)
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class TransactionCreate(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            product_names_list = data.get('products', [])
            if isinstance(product_names_list, str):
                product_names_list = [p.strip()
                                      for p in product_names_list.split(',')]
            valid_products = Product.objects.values_list('name', flat=True)
            print(valid_products)
            for product in product_names_list:
                if product.lower() not in [p.lower().strip() for p in valid_products] and product.lower() != 'unknown':
                    print(f'Product does not exist: {product}')
                    return JsonResponse({'error': f'Product does not exist: {product}'}, status=400)

            transaction = Transaction.objects.create(
                total=data['total'],
                date=data['date'],
                type=data['type']
            )

            transaction.products = product_names_list
            transaction.save()

            return JsonResponse({
                'id': transaction.id,
                'total': transaction.total,
                'date': transaction.date,
                'type': transaction.type,
                'products': product_names_list
            }, status=201)

        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error:{e}'}, status=500)


class TransactionUpdate(View):
    def put(self, request, pk):
        try:
            data = json.loads(request.body)
            transaction = Transaction.objects.get(pk=pk)

            for field in ['total', 'date', 'type']:
                if field in data:
                    setattr(transaction, field, data[field])

            product_names_list = data.get('products', [])
            if isinstance(product_names_list, str):
                product_names_list = [p.strip()
                                      for p in product_names_list.split(',')]

            valid_products = Product.objects.values_list('name', flat=True)

            for product in product_names_list:
                if product.lower() not in [p.lower().strip() for p in valid_products] and product.lower() != 'unknown':
                    return JsonResponse({'error': f'Product does not exist: {product}'}, status=400)

            transaction.products = product_names_list
            transaction.save()

            return JsonResponse({
                'id': transaction.id,
                'total': transaction.total,
                'date': transaction.date,
                'type': transaction.type,
                'products': product_names_list
            }, status=205)

        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error: {e}'}, status=500)


class ProductComparison(View):
    def get(self, request):
        try:
            products = Product.objects.filter(is_retired=False)

            product_details = []
            stock_data = []
            number_sold_data = []

            for product in products:
                product_details.append({
                    'name': product.name,
                    'price': float(product.price)
                })
                stock_data.append(product.stock)
                number_sold_data.append(product.number_sold)

            return JsonResponse({
                'labels': [p['name'] for p in product_details],
                'datasets': [
                    {
                        'label': 'Stock',
                        'data': stock_data,
                        'backgroundColor': 'rgba(54, 162, 235, 0.7)',
                        'borderColor': 'rgba(54, 162, 235, 1)',
                        'borderWidth': 1
                    },
                    {
                        'label': 'Number Sold',
                        'data': number_sold_data,
                        'backgroundColor': 'rgba(255, 99, 132, 0.7)',
                        'borderColor': 'rgba(255, 99, 132, 1)',
                        'borderWidth': 1
                    }
                ],
                'product_details': product_details
            })
        except Exception as e:
            return JsonResponse({'error': f'Internal Server Error: {e}'}, status=500)
