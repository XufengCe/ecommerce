from django.contrib import admin
from .models import *
# Register your models here.
# Inline class for OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Controls the number of empty forms to display

# Custom admin class for Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date_ordered', 'phone', 'complete', 'paid']
    list_filter = ['date_ordered', 'complete', 'paid']
    search_fields = ['customer__user__username', 'transaction_id']
    
    inlines = [OrderItemInline]  # Include the inline class here
    
# Register models with custom admin classes
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order, OrderAdmin)  # Register Order with custom admin class
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
