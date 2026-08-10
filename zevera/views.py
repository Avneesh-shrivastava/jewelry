from django.shortcuts import render
from .models import *

def home_page(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'home_page.html',context)

def new_arrivals(request):
    return render(request, 'new_arrivals.html')

def products(request, id):
    products = Product.objects.filter(category_id=id)
    category = Category.objects.get(id=id)
    extra = extra_info.objects.get(category_id=id)
    context = {
        "products" : products,
        'category' : category,
        'extra' : extra,
        } 
    return render(request, 'products.html', context)

def product_overview(request, id):
    return render(request, 'product_overview.html')