import json
from .models import *
from django.db import transaction

# This function is a helper function for the cartData function
# It is used to get the cart data from the cookies
# and return it to the cartData function

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    print('Cart:', cart)
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    cartItems = order['get_cart_items']
    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i.split('-')[0])
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL
                },
                'item_id':i,  # This is the id of the order item
                'quantity':cart[i]['quantity'],
                'description':cart[i]['description'].replace("undefined", ''),
                'get_total':total
            }
            items.append(item)
            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cartItems':cartItems, 'order':order, 'items':items}

# This function is used in store\views.py
# It is used to get the cart data from the database
# and return it to the views.py
@transaction.atomic
def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()

        print('utils.py - cartData')
        # Print the last item in the items list
        for item in items:
            print(item.product.name, 'item.product.name')

            print(item.quantity, 'item.quantity')
            print(item.description, 'item.description')

        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        print("line56 56 56 56",)
        print('cookieData:', cookieData)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems':cartItems, 'order':order, 'items':items}

@transaction.atomic
def guestOrder(request, data):
    print('User is not logged in')
    print('COOKIES:', request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer, 
        complete=False
    )

    # Create order items and set the order to the current order
    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product, 
            order=order, 
            quantity=item['quantity'],
            description=item['description']
        )
    return customer, order