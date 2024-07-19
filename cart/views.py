from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from my_store.models import Product
from django.http import JsonResponse
from django.contrib import messages

# Create your views here.

def cart_summary(request):
    #get cart
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()
    return render(request, 'cart_summary.html', {'cart_products': cart_products, 'quantities': quantities, 'totals': totals})

def cart_add(request):
    #get the cart
    cart = Cart(request)
    
    #test go post
    if request.POST.get('action') == 'post':
        #get product id
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        #lookup for product present in DB
        product = get_object_or_404(Product, id=product_id)
        
        #save to session
        cart.add(product=product, quantity=product_qty)
        
        #get cart quantity
        cart_quantity = cart.__len__()
        
        #Return response
        #response = JsonResponse({'product name':product.name})
        
        response = JsonResponse({'qty': cart_quantity})
        messages.success(request, 'Product Added To Cart!')
        return response
        

def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        #get id
        product_id = int(request.POST.get('product_id'))
        #call delete function
        cart.delete(product=product_id)
        response = JsonResponse({'product':product_id})
		#return redirect('cart_summary')
        messages.success(request, ("Product Has Been Removed..."))
        return response

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))

        cart.update(product=product_id, quantity=product_qty)

        response = JsonResponse({'qty':product_qty})
		#return redirect('cart_summary')
        messages.success(request, ("Your Product Has Been Updated..."))
        return response
