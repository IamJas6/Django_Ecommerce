from django.shortcuts import render, redirect
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from.forms import SignUpForm, UpdateUsereForm, UpdatePasswordForm, UserInfoForm
from payment.forms import ShippingAddressForm
from payment.models import ShippingAddress
from django.db.models import Q
import json
from cart.cart import Cart

# Create your views here.
def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        if not searched:
            messages.error(request, 'No Products Found...')
            return render(request, 'search.html')
        else:
            return render(request, 'search.html', {'searched':searched})
    else:
        return render(request, 'search.html')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        #did they fill out the form
        if request.method == 'POST':
            form = UpdatePasswordForm(current_user, request.POST)
            #is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Successfully Updated...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect(('update_password'))
        else:
            form = UpdatePasswordForm(current_user)
            return render(request, 'update_password.html', {'form':form})
    else:
        messages.success(request, 'You Must Be Logged In To Access That Page... ')
        return redirect('index')


def update_info(request):
    if request.user.is_authenticated:
        #get current user
        current_user = Profile.objects.get(user__id=request.user.id)
        #get users shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #get original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        #get users shipping form
        shipping_form = ShippingAddressForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, 'Your info is updated successfully')
            return redirect('index')
        return render(request, 'update_info.html', {'form':form, 'shipping_form':shipping_form})
    else:
        messages.success(request, 'You Must Be Logged In To Access That Page... ')
        return redirect('index')

def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUsereForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, 'Your profile is updated successfully')
            return redirect('index')
        return render(request, 'update_user.html', {'user_form':user_form})
    else:
        messages.success(request, 'You Must Be Logged In To Access That Page... ')
        return redirect('index')


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories":categories})


def category(request, foo):
    #replacing '-' with sapce
    foo = foo.replace('-', ' ')
    #Grab the category from url
    try:
        #look up pthe category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:
        messages.success(request, "That category doesn't exist")
        return redirect('index')
        

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product})


def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products':products})


def about(request):
    return render(request, 'about.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            current_user = Profile.objects.get(user__id=request.user.id)
            saved_cart = current_user.old_cart
            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, 'You have been logged in!')
            return redirect('index')
        else:
            messages.success(request, 'There was an error logging in. Please try again.')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    return redirect('index')
    

def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            #login the user
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Username created - Please Fill Your Details Below')
            return redirect('update_info')
        else:
            messages.success(request, 'Password Did Not Match, Please try again.')
            return redirect('register')
    else:
        return render(request, 'register.html', {'form':form})