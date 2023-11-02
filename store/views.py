from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cartData, cookieCart, guestOrder
from twilio.twiml.voice_response import VoiceResponse
import os
from twilio.rest import Client
from dotenv import load_dotenv
from django.db import transaction
import time




# Get the current working directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Combine the current directory with the relative path to .env
relative_path_to_env = os.path.join(current_directory, '.env')

# Load environment variables from .env file with relative path
load_dotenv(dotenv_path=relative_path_to_env)

def store(request):

    data = cartData(request)
    cartItems = data['cartItems']

    
    hotdogs = Product.objects.filter(category='Hotdogs')
    soups = Product.objects.filter(category='Soups')
    desserts = Product.objects.filter(category='Desserts')
    sandwiches = Product.objects.filter(category='Sandwiches')
    sandwiches = sorted(sandwiches, key=custom_order)
    print(sandwiches, 'sandwiches')
    drinks = Product.objects.filter(category='Drinks')
    sides = Product.objects.filter(category='Sides')
    breakfast = Product.objects.filter(category='Breakfast')
    products = [hotdogs, soups, desserts, drinks, sides, breakfast]

    print(hotdogs, 'hotdogs')
    print(soups, 'soups')

    context = {'products': products, 'cartItems': cartItems, 'hotdogs': hotdogs, 'soups': soups, 'desserts': desserts, 'sandwiches': sandwiches, 'drinks': drinks, 'sides': sides, 'breakfast': breakfast}
    return render(request, 'store/store.html', context)
# This function is used to sort the sandwiches by name
def custom_order(product):
    name_lower = product.name.lower()
    base_name = name_lower
    if name_lower.endswith(' - combo'):
        # Remove the ' - combo' from the name and replace it with 'a'
        base_name = name_lower[:-len(' - combo')] + 'a'
        
    elif name_lower.endswith(' - large'):
        base_name = name_lower[:-len(' - large')] + 'b'

    elif name_lower.endswith(' - regular'):
        base_name = name_lower[:-len(' - regular')] + 'c'
        
    return base_name, name_lower




def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def verify(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'assets/index.html', context)
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def send_otp(request):
    data = json.loads(request.body)
    phone_number = data['phone_number']
    # print(phone_number, 'phone_number')
    # print(type(phone_number), 'type phone_number')


    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    verify_sid = os.getenv('VERIFY_SERVICE_SID')
    print(account_sid, '57:sid')

    client = Client(account_sid, auth_token)

    # verification = client.verify \
    #                  .v2 \
    #                  .services(verify_sid) \
    #                  .verifications \
    #                  .create(to='+1'+ phone_number, channel='sms')
    # print(verification.status)
    # if verification.status == 'pending':
    #     return JsonResponse('Otp sent', safe=False)
    # else:
    #     return JsonResponse('Otp not sent', safe=False)

    return JsonResponse('Otp sent', safe=False)

def verify_otp(request):
    data = json.loads(request.body)
    print(request, 'request')
    print(data, 'data')

    phone_number = data['paymentData']['phone_number']
    otp_number = data['paymentData']['otp_number']
    print(phone_number, 'phone_number')
    print(otp_number, 'otp_number')
    print(type(phone_number), 'type phone_number')
    print(type(otp_number), 'type otp_number')

    account_sid = os.getenv('ACCOUNT_SID')
    auth_token = os.getenv('AUTH_TOKEN')
    verify_sid = os.getenv('VERIFY_SERVICE_SID')

    client = Client(account_sid, auth_token)
    # verification_check = client.verify \
    #                         .v2 \
    #                         .services(verify_sid) \
    #                         .verification_checks \
    #                         .create(to='+1'+ phone_number, code=otp_number)

    # print(verification_check.status)   
    # if verification_check.status == 'approved':
    #     processOrder(request)
    #     return JsonResponse('Otp verified', safe=False)
    # else:
    #     return JsonResponse('Otp not verified', safe=False)



    if processOrder(request).status_code == 200:
        return JsonResponse('Otp verified', safe=False)
    else:
        return JsonResponse('Otp not verified', safe=False)


# This function works atomically
# It is used to get the cart data from the database
# and return it to the views.py
@transaction.atomic
def updateItem(request):
    data = json.loads(request.body)
    # print("views.py - updateItem", data)
    # print(data['productId'])
    productId = data['productId']
    action = data['action']
    # print('Action:', action)
    # print('Product Id:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # print(order, 'order')
    # print(created, 'created')

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product, description=data['description'])

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    print(orderItem.quantity, 'orderItem.quantity')
    orderItem.save()
    # print(orderItem.quantity, 'orderItem.quantity')
    # print(orderItem, 'orderItem')

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


@csrf_exempt
@transaction.atomic
def processOrder(request):
    # The transaction_id is used to identify the order and the payment
    # Time in usec
    transaction_id = datetime.datetime.now()
    print(transaction_id, 'transaction_id')
    data = json.loads(request.body)
    print(data, 'data')
    
    


    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False) # get_or_create() returns a tuple of (object, created), where object is the retrieved or created object and created is a boolean specifying whether a new object was created.
        
    else:

        customer, order = guestOrder(request, data)
        print(request, 'request')
        print(customer, 'customer')
        print(order, 'order')
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    order.paid = data['paid']
    print(total, 'total')
    print(order.get_cart_total, 'order.get_cart_total')
    if total == float(order.get_cart_total):
        order.complete = True
    else:
        return JsonResponse('Payment not complete!', safe=False)
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer, 
            order=order, 
            address=data['shipping']['address'], 
            city=data['shipping']['city'], 
            state=data['shipping']['state'], 
            zipcode=data['shipping']['zipcode']
        )
    
    return JsonResponse('Payment complete!', safe=False)
from django.contrib.auth import authenticate
from rest_framework import serializers
# Define a serializer for the Order model
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'  # Include all fields from the Order model

# This method is an API for store ower to get the order information
# Only return the orders if the user is admin
def orderInfo(request):
    print(request, 'request')
    print(request.GET, 'request.GET')
    username = request.GET.get('username')
    password = request.GET.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        serializer = OrderSerializer(Order.objects.all(), many=True)
        return JsonResponse(serializer.data, safe=False)
    else:
        return JsonResponse('User is not admin', safe=False)
