from django.shortcuts import render
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import hmac
import hashlib
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.template.loader import render_to_string

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))



def home_page(request):
    categories = Category.objects.all()
    best_sellers = OrderItem.objects.values('product_id')
    best_sellers = best_sellers.annotate(count=Count('product_id'))
    best_sellers = best_sellers.order_by('-count')
    print(best_sellers)
    
    products = Product.objects.filter( id__in=[item['product_id'] for item in best_sellers] )
    print(products)
    


    global cart_items_no
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        cart_items_no = cart.count()
    else:
        cart = []
        cart_items_no = 0

    context = {
        'categories' : categories,
        'cart_items_no' : cart_items_no,
        'best_sellers': products,
    }
    return render(request, 'home_page.html',context)

def new_arrivals(request):
    return render(request, 'new_arrivals.html')

def products(request, id):
    products = Product.objects.filter(category_id=id)
    category = Category.objects.get(id=id)
    extra = extra_info.objects.get(category_id=id)

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user = request.user)
        cart_items_no = len(cart)
    else:
        cart = []
        cart_items_no = 0
        
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
    if request.user.is_authenticated:
        no_of_cart_items = len(Cart.objects.filter(user = request.user))
    else:
        no_of_cart_items = 0

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
            dynamic_price=price,
            size=size,  
            defaults = {
                "quantity":quantity,
            }
        )
        if not created:
            
            current_obj = Cart.objects.get(products_id=product_id)
            current_obj.quantity += quantity 
            current_obj.save()
  
        
        print(f"Adding {quantity} of {product.name} to cart worth rs. {price}")  # temporary, just to confirm it's working

    return redirect('product_overview', id=product_id)

@login_required(login_url='/login/')
def cart(request):
    cart_items = Cart.objects.filter(user = request.user)
    no_of_cart_items = len(cart_items)
    prod_prices = cart_items.values_list('dynamic_price', flat=True)
    subtotal = sum(prod_prices)
    coupon_code = ''
    products = Product.objects.order_by('-id')[:5]
    
    
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
        "coupon_type" : coupon_code,
        "products" : products
    }
     
    return render(request, 'cart.html',context)

@login_required(login_url='/login/')
def remove_cart(request, rm_id):
    Cart.objects.filter(id=rm_id).delete()
    return redirect('cart')


@login_required(login_url='/login/')
def update_cart(request, cart_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        cart_item.quantity = quantity
        cart_item.dynamic_price = cart_item.price * cart_item.quantity
        cart_item.save()

        cart_items = Cart.objects.filter(user=request.user)
        cart_subtotal = sum(c.dynamic_price for c in cart_items)

        if request.session['coupon_code'] == "GET20":
            discount = round(cart_subtotal * 0.20, 2)

        cart_total = float(cart_subtotal - discount)      

    item_html = render_to_string('partials/cart_item.html', {'cart': cart_item}, request=request)
    totals_html = render_to_string('partials/cart_totals_oob.html', {'cart_total': cart_total, 'cart_subtotal':cart_subtotal}, request=request)

    return HttpResponse(item_html + totals_html)
    

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.info(request, "Your bag is empty.")
        return redirect('cart')

    subtotal = sum(item.price * item.quantity for item in cart_items)
    shipping = 0
    discount = 0
    total = subtotal + shipping - discount

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'no_of_cart_items': cart_items.count(),
        'subtotal': subtotal,
        'shipping': shipping,
        'discount': discount,
        'total': total,
    })

@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')

    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your bag is empty.")
        return redirect('cart')

    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()
    address_line1 = request.POST.get('address_line1', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip()
    pincode = request.POST.get('pincode', '').strip()
    landmark = request.POST.get('landmark', '').strip()
    payment_method = request.POST.get('payment_method', '')

    required_fields = [full_name, phone, email, address_line1, city, state, pincode, payment_method]
    if not all(required_fields):
        messages.error(request, "Please fill in all required fields.")
        return redirect('checkout')

    if payment_method not in ('razorpay', 'cod'):
        messages.error(request, "Please select a valid payment method.")
        return redirect('checkout')

    subtotal = sum(item.price * item.quantity for item in cart_items)
    total = subtotal  # add shipping/discount logic here if needed

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            email=email,
            address_line1=address_line1,
            city=city,
            state=state,
            pincode=pincode,
            landmark=landmark,
            payment_method=payment_method,
            status='pending',
            subtotal=subtotal,
            total=total,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.products,
                product_name=item.product,
                price=item.price,
                quantity=item.quantity,
                size=item.size,
            )

        cart_items.delete()

    if payment_method == 'cod':
        order.status = 'confirmed'
        order.save()
        return redirect('order_confirmation', order_id=order.id)

    # razorpay: redirect to a payment view that creates the Razorpay order
    # and renders their checkout widget, then verifies payment on callback
    return redirect('razorpay_payment', order_id=order.id)


@login_required
def razorpay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'pending':
        messages.info(request, "This order has already been processed.")
        return redirect('order_confirmation', order_id=order.id)

    # Razorpay needs the amount in paise (smallest currency unit), as an integer
    amount_paise = int(order.total * 100)

    razorpay_order = razorpay_client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': 1,
        'receipt': f'order_{order.id}',
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    return render(request, 'razorpay_payment.html', {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount_paise': amount_paise,
    })

@csrf_exempt
@login_required
def verify_payment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id, user=request.user)

    # Verify the signature ourselves — never trust the frontend's word that payment succeeded
    generated_signature = hmac.new(
        key=settings.RAZORPAY_KEY_SECRET.encode(),
        msg=f'{razorpay_order_id}|{razorpay_payment_id}'.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        order.status = 'cancelled'
        order.save()
        return JsonResponse({'success': False, 'error': 'Payment verification failed'}, status=400)

    order.razorpay_payment_id = razorpay_payment_id
    order.razorpay_signature = razorpay_signature
    order.status = 'paid'
    order.save()

    return JsonResponse({'success': True, 'redirect_url': f'/order-confirmation/{order.id}/'})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def remove_coupon(request):
    if request.method == 'POST':
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
    return redirect('cart')