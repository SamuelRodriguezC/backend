from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser


# ----------------------- USUARIO ----------------------- 
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.email
    
# ----------------------- CATEGORÍA ----------------------- 
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.FileField(upload_to="category_img", blank=True, null=True)

    def __str__(self):
        return self.name

    # Genera un slug único basado en el nombre antes de guardar la categoría.
    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name) #Convierte el texto en una versión amigable para URLs (reemplazar espacios por guines y todas las letras a minusculas)
            unique_slug = self.slug
            counter = 1
            # Si ya existe un producto con ese slug 
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        
        super().save(*args, **kwargs)

# ----------------------- PRODUCTO ----------------------- 
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="product_img", blank=True, null=True)
    featured = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name="products",  blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):

        # Genera automáticamente un slug único basado en el nombre si no existe.

        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
            self.slug = unique_slug
        
        super().save(*args, **kwargs)

# ----------------------- CARRITO -----------------------
class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cart_code


# ----------------------- ITEM DEL CARRITO -----------------------
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cartitems")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="item")
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.cart_code}"
    


# ----------------------- RESEÑA -----------------------
class Review(models.Model):

    RATING_CHOICES = [
        (1, '1 - Malo'),
        (2, '2 - Regular'),
        (3, '3 - Bueno'),
        (4, '4 - Muy Bueno'),
        (5, '5 - Excelente'),
    ]


    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"
    
    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-created"]


# ----------------------- VALORACIÓN DE PRODUCTO -----------------------
class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='rating')
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.average_rating} ({self.total_reviews} reviews)"



# ----------------------- LISTA DE DESEOS -----------------------
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlists")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist")
    created = models.DateTimeField(auto_now_add=True) 

    class Meta:
        unique_together = ["user", "product"]  # No se puede duplicar un mismo producto

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    


# ----------------------- ORDEN -----------------------
class Order(models.Model):
    stripe_checkout_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Paid", "Paid")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.stripe_checkout_id} - {self.status}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Order {self.product.name} - {self.order.stripe_checkout_id}"
    


# ----------------------- DIRECCIÓN DE CLIENTE -----------------------
class CustomerAddress(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return f"{self.customer.email} - {self.street} - {self.city}"