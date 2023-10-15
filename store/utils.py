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

            product = Product.objects.get(id=cart[i]['productId'])            
            
            price = calculate_price(product, cart[i]['description'])
            total = price * cart[i]['quantity']
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':price,
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
        name=name,
        # email=email,
    )
    # customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer, 
        phone=data['paymentData']['phone_number'],
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

def calculate_price(product, description):
    # Sides that cost extra
    sides = ['Slaw', 'Potato Salad', 'Macaroni Salad', 'Deviled Eggs', 'Fries']
    # Special case that cost different, Egg Salad Sandwich, Potato Salad Sandwich, and Grilled Cheese Sandwich
    # BLT sandwich, egg salad sandwich, pimento cheese sandwich, and grilled cheese sandwich are special cases
    # BLT sandwich[7.25, 8.75], egg salad sandwich[5.50, 6.75], pimento cheese sandwich[5.50, 6.75], and grilled cheese sandwich[4.25, 5.40]
    # BLT sandwich combo[11.50, 13.00], egg salad sandwich combo[9.55, 11.00], pimento cheese sandwich combo[8.90, 10.05], and grilled cheese sandwich combo[7.65, 8.80]
    
    specialCase = {'BLT Sandwich': [Decimal('7.25'), Decimal('8.75')], 'Egg Salad Sandwich': [Decimal('5.50'), Decimal('6.75')], 'Pimento Cheese Sandwich': [Decimal('5.50'), Decimal('6.75')], 'Grilled Cheese Sandwich': [Decimal('4.25'), Decimal('5.40')]}
    specialCaseCombo = {'BLT Sandwich Combo': [Decimal('11.50'), Decimal('13.00')], 'Egg Salad Sandwich Combo': [Decimal('9.55'), Decimal('11.00')], 'Pimento Cheese Sandwich Combo': [Decimal('8.90'), Decimal('10.05')], 'Grilled Cheese Sandwich Combo': [Decimal('7.65'), Decimal('8.80')]}
    price = product.price
    # Handle special case first - special case and special case combo
    if product.name in specialCase or product.name in specialCaseCombo:
        # Combo, Large
        if product.size and "Large" in description and product.combo:
            price = specialCaseCombo[product.name][1]
        # Not combo, Large
        elif product.size and "Large" in description:
            price = specialCase[product.name][1]
        # Combo, Regular
        elif product.size and product.combo:
            price = specialCaseCombo[product.name][0]
        # Not combo, Regular
        elif product.size:
            price = specialCase[product.name][0]
        # Add 0.4 to the price if the side is in the description
        if any(side in description for side in sides):
            price += Decimal('0.4')
        return price
    # Regular combo and Large combo
    if product.combo:
        if product.size and "Large" in description:
            price += Decimal('1.5')
        if any(side in description for side in sides):
            price += Decimal('0.4')
        return price
    
    # Regular and Large
    if product.size:
        if "Large" in description:
            price += Decimal('1.5')
        if any(side in description for side in sides):
            price += Decimal('0.4')
        return price

    # Special case for sides - Large sides cost 3.00 more
    if product.category == 'Sides' and product.size:
        if "Large" in description:
            if product.name == "Deviled Eggs":
                return product.price + Decimal('3.00')
            elif product.name == "Fries":
                return product.price + Decimal('0.75')
            else:
                return product.price + Decimal('3.25')
    
    # Special case for drinks - Large drinks cost 0.50 more
    if product.category == 'Drinks' and product.size:
        if "Large" in description:
            return product.price + Decimal('0.50')
    return product.price



