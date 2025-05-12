# core/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Custom User with role
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

# 2. Categories
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

# 3. Products
class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.name

# 4. Orders & Items
class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    PAID = 'paid'
    UNPAID = 'unpaid'
    PAYMENT_STATUS = ((PAID, 'Paid'), (UNPAID, 'Unpaid'))
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default=UNPAID)

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    @property
    def total_price(self):
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        # On save, decrement product stock
        if not self.pk:  # new item
            if self.quantity > self.product.stock:
                raise ValueError('Insufficient stock')
            self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)