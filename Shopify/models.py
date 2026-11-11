
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import uuid


def generate_unique_slug(instance, value):

    base_slug = slugify(value) or "item"
    slug = base_slug
    counter = 1

    ModelClass = instance.__class__

    while ModelClass.objects.filter(
        slug=slug
    ).exclude(pk=instance.pk).exists():

        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# A. CATEGORY MODEL
class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_unique_slug(
                self, self.name
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def is_main_category(self):
        return self.parent is None


# B. PRODUCT MODEL
class Product(models.Model):

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    image = models.ImageField(
        upload_to='products/'
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_unique_slug(
                self, self.name
            )

        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


# C. ORDER MODEL
class Order(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    full_name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20
    )

    address = models.TextField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.order_number:
            self.order_number = (
                f"ORD-{uuid.uuid4().hex[:8].upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


# D. ORDER ITEM MODEL
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_subtotal(self):
        return self.quantity * self.price
