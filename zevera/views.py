from django.shortcuts import render
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404



def home_page(request):
    categories = Category.objects.all()
    cart = Cart.objects.filter(user_id = request.user)
    cart_items_no = len(cart)

    context = {
        'categories' : categories,
        'cart_items_no' : cart_items_no
    }
    return render(request, 'home_page.html',context)

def new_arrivals(request):
    return render(request, 'new_arrivals.html')

def products(request, id):
    products = Product.objects.filter(category_id=id)
    category = Category.objects.get(id=id)
    extra = extra_info.objects.get(category_id=id)
    cart = Cart.objects.filter(user_id = request.user)
    cart_items_no = len(cart)
    context = {
        "products" : products,
        'category' : category,
        'extra' : extra,
        'cart_items_no': cart_items_no
        } 
    return render(request, 'products.html', context)


def product_overview(request, id):
    product = Product.objects.filter(id=id).first()
    products = Product.objects.all()
    category = Category.objects.get(id=id)
    reviews = Reviews.objects.filter(product=id)
    people_reviewed = len(reviews)
    cart = Cart.objects.filter(products_id=id)
    print(cart)
    no_of_cart_items = len(Cart.objects.filter(user_id = request.user))
    product_images = ProductImage.objects.all()
    

    try:
        no_of_stars = list(reviews.values_list('stars',flat=True))
        five = four = three = two = one = 0
        for i in no_of_stars:
            if i == 5:
                five = five + 1
            if i == 4:
                four = four + 1
            if i == 3:
                three = three + 1
            if i == 2:
                two = two + 1
            if i == 1:
                one = one + 1

        no_of_stars = len(no_of_stars)
        percentage_five = int((five/no_of_stars)*100)
        percentage_four = int((four/no_of_stars)*100)
        percentage_three = int((three/no_of_stars)*100)
        percentage_two = int((two/no_of_stars)*100)
        percentage_one = int((one/no_of_stars)*100)

        review_score = (five*5 + four*4 + three*3 + two*2 + one)/no_of_stars
        review_score = round(review_score, 1)
    except ZeroDivisionError:
        percentage_five = percentage_four = percentage_three = percentage_two = percentage_one = review_score = 0


    # Rating's POST
    if request.method == "POST":
        stars = request.POST.get("rating")
        review = request.POST.get("review_text")

        
        Reviews.objects.create(
            product=product, 
            user=request.user,
            review=review,
            stars=stars
        )
        return redirect(f"/product-overview/{id}")
    
    context = {
        "product" : product,
        'category' : category,
        "products" : products,
        "reviews" : reviews,

        "percentage_five" : percentage_five,
        "percentage_four": percentage_four,
        "percentage_three": percentage_three,
        "percentage_two": percentage_two,
        "percentage_one": percentage_one,

        "review_score" : review_score,
        "people_reviewed":people_reviewed,
        "no_of_cart_items":no_of_cart_items,

        "cart": cart,

        "product_images": product_images

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



@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        price = request.POST.get('prod_price')
        size = request.POST.get('size',6)
 
        

        print(size)
        print(type(product))

        obj, created = Cart.objects.get_or_create(
            user = request.user,
            products=product,
            product=product,
            price=price,
            size=size,  
            defaults = {
                "quantity":quantity,
            }
        )
        if not created:
            
            current_obj = Cart.objects.get(products_id=product_id)
            current_obj.quantity += quantity 
            current_obj.save()
            # current_obj.price = current_obj.price * current_obj.quantity
            # current_obj.save()   
        


        print(f"Adding {quantity} of {product.name} to cart worth rs. {price}")  # temporary, just to confirm it's working

    return redirect('product_overview', id=product_id)

@login_required(login_url='/login/')
def cart(request):
    cart_items = Cart.objects.filter(user_id = request.user)
    no_of_cart_items = len(cart_items)
    prod_prices = cart_items.values_list('price', flat=True)
    subtotal = sum(prod_prices)
    coupon_code = ''
    
    
    if request.method =='POST':
        coupon_code = request.POST.get('coupon_code')
        coupon_code = coupon_code.upper()
        if coupon_code == "GET20":
            request.session['coupon_code'] = "GET20"
        else:
            request.session.pop('coupon_code', None)
        return redirect('cart')
        
    coupon_code = request.session.get('coupon_code')
    discount = 0
    if coupon_code == "GET20":
        discount = round(subtotal * 0.20, 2)
    
    total_price = float(subtotal - discount)   

    context = {
        "cart_items":cart_items,
        "no_of_cart_items": no_of_cart_items,
        "subtotal":subtotal,
        "discount":discount,
        "total_price": total_price,
    }
     
    return render(request, 'cart.html',context)

@login_required(login_url='/login/')
def remove_cart(request, rm_id):
    Cart.objects.filter(id=rm_id).delete()
    return redirect('cart')


@login_required(login_url='/login/')
def update_cart(request, cart_id):

    if request.method == 'POST':

        data = json.loads(request.body)

        quantity = int(data.get('quantity'))

        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Quantity must be at least 1'
            })

        if quantity > 10:
            return JsonResponse({
                'success': False,
                'error': 'Maximum quantity is 10'
            })


        #This is where the data get's updated in the Postgresql
        cart = get_object_or_404(Cart, id=cart_id)
        cart.quantity = quantity
        cart.save()

        return JsonResponse({
            'success': True,
            'quantity': cart.quantity
        })

    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })
