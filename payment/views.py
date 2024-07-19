from django.shortcuts import render, redirect
from django.contrib import messages
from cart.cart import Cart
from payment.forms import ShippingAddressForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItems
from django.contrib.auth.models import User
from my_store.models import Product, Profile
import datetime

# Create your views here.
def shippingaddress(request):
    return render(request, 'payment/shippingaddress.html')

def checkout(request):
    #get cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form':shipping_form})
    else:
        shipping_form = ShippingAddressForm(request.POST or None)
        return render(request, 'payment/checkout.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form':shipping_form})


def billing_info(request):
    if request.POST:
        #get cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        #create session with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        #Check user is logged in
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info':request.POST, 'billing_form':billing_form})

        else:
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_info':request.POST, 'billing_form':billing_form})

        shipping_form = request.POST
        return render(request, 'payment/billing_info.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals, 'shipping_form':shipping_form})
    
    else:
        messages.success(request, "Access Denied")
        return redirect('index')


def process_order(request):
    if request.POST:
        #get cart
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        #get billing info from last page
        payment_form = PaymentForm(request.POST or None)

        #get shipping session data
        my_shipping = request.session.get('my_shipping')

        #gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        #create shipping address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        #create order
        if request.user.is_authenticated:
            #if logged in
            user = request.user
            #creating order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            
            #creating order items
            order_id = create_order.pk

            #get product info
            for product in cart_products():
                product_id = product.id
                #get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                
                #get quantity 
                for key, value in quantities().items():
                    if int(key) == product.id:
                        #create order item
                        create_order_item = OrderItems(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            #delete cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    #delete key
                    del request.session[key]

            #delete cart from database
            current_user = Profile.objects.filter(user__id=request.user.id)
            current_user.update(old_cart="")

            messages.success(request, "Order Placed Successfully")
            return redirect('index')
        else:
            #not logged in
            #creating order
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            #creating order items
            order_id = create_order.pk

            #get product info
            for product in cart_products():
                product_id = product.id
                #get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                
                #get quantity 
                for key, value in quantities().items():
                    if int(key) == product.id:
                        #create order item
                        create_order_item = OrderItems(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()

            #delete cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    #delete
                    del request.session[key]
                        
            messages.success(request, "Order Placed Successfully")
            return redirect('index')
    else:
        messages.success(request, "Access Denied")
        return redirect('index')

    
def unshipped_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            #get the order
            order = Order.objects.filter(id=num)
            #update order
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)
            messages.success(request, "Shipping Status Updated")
            return redirect('index')
        return render(request, 'payment/unshipped_page.html', {'orders':orders})
    else:
        messages.error(request, 'Access Denied')
        return redirect('index')


def shipped_page(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            #get the order
            order = Order.objects.filter(id=num)
            #update order
            order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('index')
        return render(request, 'payment/shipped_page.html', {'orders':orders})
    else:
        messages.error(request, 'Access Denied')
        return redirect('index')


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #get the orders
        order = Order.objects.get(id=pk)
        #get the order items
        items = OrderItems.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            #check true or false
            if status == "true":
                #get the order
                order = Order.objects.filter(id=pk)
                #update order
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped = now)
            else:
                #get the order
                order = Order.objects.filter(id=pk)
                #update order
                order.update(shipped=False)
            messages.success(request, "Shipping Status Updated")
            return redirect('index')
        return render(request, 'payment/orders.html', {"order":order, "items":items})
    else:
        messages.error(request, 'Access Denied')
        return redirect('index')