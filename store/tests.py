# Create your tests here.
import time
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Customer, Product, Order, OrderItem
import threading
import json

class AtomicTransactionTest(TestCase):
    def setUp(self):
        # Create a user and customer
        self.user = User.objects.get_or_create(username='admin', password='123456')[0]
        self.customer = Customer.objects.create(user=self.user)

    def test_atomic_transaction(self):
        # Define the data for your test
        data = {'form': {'name': 'test', 'email': None, 'total': '3.50'}, 'shipping': {'address': None, 'city': None, 'state': None, 'zipcode': None, 'country': None}, 'paymentData': {'phone_number': 9293008695, 'otp_number': 123456}, 'paid': False}

        # Define the method you want to test
        def update_item():
            # Simulate a request with data
            request = self.client.post('/verify_otp/', json.dumps(data), content_type='application/json')
            return request

        # Create a list to hold thread objects
        threads = []

        # Number of concurrent calls to simulate
        num_threads = 10

        # Define a function for each thread to call
        def thread_function():
            response = update_item()
            # Add assertions based on the expected behavior of your view
            # self.assertEqual(response.status_code, 200)

        for _ in range(num_threads):
            # Create and start a thread
            thread = threading.Thread(target=thread_function)
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Add additional assertions to check the final state of your data
        # For example, check if the order and order item are as expected
