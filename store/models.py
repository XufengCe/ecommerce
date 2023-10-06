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
    size = models.BooleanField(default=True, null=True, blank=True)
    combo = models.BooleanField(default=False, null=True, blank=True)
    digital = models.BooleanField(default=True, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
         return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True) # ForeignKey means that each order can have only one customer but each customer can have multiple orders
    date_ordered = models.DateTimeField(auto_now_add=True) # auto_now_add=True means that the date_ordered field will be automatically set to the current date and time when a new order is created
    complete = models.BooleanField(default=False, null=True, blank=True) # BooleanField means that each order can be either complete or not complete
    transaction_id = models.CharField(max_length=200, null=True)
    paid = models.BooleanField(default=False, null=True, blank=True) # BooleanField means that each order can be either paid or not paid
    phone = models.CharField(max_length=200, null=True, blank=True)
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
    

    def get_cart_total_admin(self):
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
        
        self.price = self.calculate_price()
        super().save(*args, **kwargs)
    date_added = models.DateTimeField(auto_now_add=True) # auto_now_add=True means that the date_added field will be automatically set to the current date and time when a new order item is created
    
    def calculate_price(self):
        # Sides that cost extra
        sides = ['Slaw', 'Potato Salad', 'Macaroni Salad', 'Deviled Eggs', 'Fries']
        # Special case that cost different, Egg Salad Sandwich, Potato Salad Sandwich, and Grilled Cheese Sandwich
        # BLT sandwich, egg salad sandwich, pimento cheese sandwich, and grilled cheese sandwich are special cases
        # BLT sandwich[7.25, 8.75], egg salad sandwich[5.50, 6.75], pimento cheese sandwich[5.50, 6.75], and grilled cheese sandwich[4.25, 5.40]
        # BLT sandwich combo[11.50, 13.00], egg salad sandwich combo[9.55, 11.00], pimento cheese sandwich combo[8.90, 10.05], and grilled cheese sandwich combo[7.65, 8.80]
        
        specialCase = {'BLT Sandwich': [Decimal('7.25'), Decimal('8.75')], 'Egg Salad Sandwich': [Decimal('5.50'), Decimal('6.75')], 'Pimento Cheese Sandwich': [Decimal('5.50'), Decimal('6.75')], 'Grilled Cheese Sandwich': [Decimal('4.25'), Decimal('5.40')]}
        specialCaseCombo = {'BLT Sandwich Combo': [Decimal('11.50'), Decimal('13.00')], 'Egg Salad Sandwich Combo': [Decimal('9.55'), Decimal('11.00')], 'Pimento Cheese Sandwich Combo': [Decimal('8.90'), Decimal('10.05')], 'Grilled Cheese Sandwich Combo': [Decimal('7.65'), Decimal('8.80')]}
        price = self.product.price
        # Handle special case first
        if self.product.name in specialCase or self.product.name in specialCaseCombo:
            # Combo, Large
            if self.product.size and "Large" in self.description and self.product.combo:
                price = specialCaseCombo[self.product.name][1]
            # Not combo, Large
            elif self.product.size and "Large" in self.description:
                price = specialCase[self.product.name][1]
            # Combo, Regular
            elif self.product.size and self.product.combo:
                price = specialCaseCombo[self.product.name][0]
            # Not combo, Regular
            elif self.product.size:
                price = specialCase[self.product.name][0]
            # Add 0.4 to the price if the side is in the description
            if any(side in self.description for side in sides):
                price += Decimal('0.4')
            return price
        # For every combo, if the side is in the description, add 0.4 to the price
        # For every combo, if the size is regular, add 0.4 to the price
        if self.product.combo:
            if self.product.size and "Large" in self.description:
                price += Decimal('1.5')
            if any(side in self.description for side in sides):
                price += Decimal('0.4')
            return price
            
        if self.product.category == 'Sides' and self.product.size:
            if "Large" in self.description:
                if self.product.name == "Deviled Eggs":
                    return self.product.price + Decimal('3.00')
                elif self.product.name == "Fries":
                    return self.product.price + Decimal('0.75')
                else:
                    return self.product.price + Decimal('3.25')

        if self.product.category == 'Drinks' and self.product.size:
            if "Large" in self.description:
                return self.product.price + Decimal('0.50')
        return self.product.price
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