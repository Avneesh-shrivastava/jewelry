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