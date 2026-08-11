from django.shortcuts import render
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect

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
    product = Product.objects.filter(id=id).first()
    products = Product.objects.all()
    category = Category.objects.get(id=id)

    if request.method == "POST":
        stars = request.POST.get("rating")
        review = request.POST.get("review_text")

        
        Reviews.objects.create(
            user=request.user,
            review=review,
            stars=stars
        )
    
    context = {
        "product" : product,
        'category' : category,
        "products" : products,

        }
    
    return render(request, 'product_overview.html',context)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home_page')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home_page')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home_page')