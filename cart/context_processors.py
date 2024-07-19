from .cart import Cart

#create context processors so our cart can work on all pages of site
def cart(request):
    #return default data from our cart
    return {'cart': Cart(request)}