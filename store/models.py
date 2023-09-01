from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE) # OneToOneField means that each customer can have only one user and each user can have only one customer
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
         return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2) # max_digits=7 means that the maximum number of digits allowed in the price field is 7 and decimal_places=2 means that the maximum number of decimal places allowed in the price field is 2
    size = models.CharField(max_length=50, choices=[('small', 'Small'), ('large', 'Large'),('combo-small', 'Combo-Samll'),('combo-large','Combo-Large')],default='small')
    digital = models.BooleanField(default=True, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    # description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
         return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    
    def calculate_price(self):
        if self.size == 'small':
            return self.price
        else:
            return self.price + 1.5



class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True) # ForeignKey means that each order can have only one customer but each customer can have multiple orders
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=True) # BooleanField means that each order can be either complete or not complete
    transaction_id = models.CharField(max_length=200, null=True)
    paid = models.BooleanField(default=False, null=True, blank=True) # BooleanField means that each order can be either paid or not paid

    def __str__(self):
        return str(self.id)
    
    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all() # orderitem_set is a reverse relationship from the OrderItem model to the Order model
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self): # @property means that this method can be accessed like an attribute
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])

        return total
    
    @property
    def get_cart_items(self): # @property means that this method can be accessed like an attribute
        orderitems = self.orderitem_set.all() # orderitem_set is a reverse relationship from the OrderItem model to the Order model
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True) # ForeignKey means that each order item can have only one product but each product can have multiple order items
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True) # ForeignKey means that each order item can have only one order but each order can have multiple order items
    quantity = models.IntegerField(default=0, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True) # max_digits=7 means that the maximum number of digits allowed in the price field is 7 and decimal_places=2 means that the maximum number of decimal places allowed in the price field is 2
    # extra charge if the size is combo and side is Slaw, potato salad, or macaroni salad, deviled eggs, or fries.
    def save(self, *args, **kwargs):
        if self.product.size in ['combo-small', 'combo-large']:
            if any(desc in self.description for desc in ['slaw', 'potato salad', 'macaroni salad', 'deviled eggs', 'fries']):
                self.price = self.product.price + Decimal('0.4')
            else:
                self.price = self.product.price
        else:
            self.price = self.product.price
        super().save(*args, **kwargs)
    date_added = models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self):
        self.save()
        total = self.price * self.quantity
        return total
    
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True) # ForeignKey means that each shipping address can have only one customer but each customer can have multiple shipping addresses
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True) # ForeignKey means that each shipping address can have only one order but each order can have multiple shipping addresses
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True) # auto_now_add=True means that the date_added field will be automatically set to the current date and time when a new shipping address is created

    def __str__(self):
        return self.address