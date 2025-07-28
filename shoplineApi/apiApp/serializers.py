from rest_framework import serializers 
from django.contrib.auth import get_user_model
from .models import Cart, CartItem, CustomerAddress, Order, OrderItem, Product, Category, ProductRating, Review, Wishlist


# LOS SERIALIZERS SON UTILIZADOS PARA CONVERTIR LOS MODELOS A JSON Y VICEVERSA
# SON IMPORTANTES PARA EL TRABAJO CON API REST


# -------------------------- LISTA DE PRODUCTOS --------------------------
class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "slug", "image", "price"]



# -------------------------- USUARIO --------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # Obtener la clase modelo activa en el proyecto  AUTH_USER_MODEL (settings.py)
        model = get_user_model()
        fields = ["id", "email", "username", "first_name", "last_name", "profile_picture_url"]

    
# -------------------------- RESEÑAS --------------------------
class ReviewSerializer(serializers.ModelSerializer):
     # Muestra los datos del usuario, pero no permite modificarlos desde este serializer
    user = UserSerializer(read_only=True)
    class Meta:
        model = Review 
        fields = ["id", "user", "rating", "review", "created", "updated"]

# -------------------------- VALORACIONES --------------------------
class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating 
        fields =[ "id", "average_rating", "total_reviews"]



# -------------------------- DETALLES DE PRODUCTOS  --------------------------
class ProductDetailSerializer(serializers.ModelSerializer):

    reviews = ReviewSerializer(read_only=True, many=True)
    rating = ProductRatingSerializer(read_only=True)
    poor_review = serializers.SerializerMethodField()
    fair_review = serializers.SerializerMethodField()
    good_review = serializers.SerializerMethodField()
    very_good_review = serializers.SerializerMethodField()
    excellent_review = serializers.SerializerMethodField()

    similar_products = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ["id", "name", "description", "slug", "image", "price", "reviews", "rating", "similar_products", "poor_review", "fair_review", "good_review",
                  "very_good_review", "excellent_review"]
        
    # Obtiene productos de la misma categoría (excepto el actual) y los convierte en JSON con un serializer
    def get_similar_products(self, product):
        products = Product.objects.filter(category=product.category).exclude(id=product.id)
        serializer = ProductListSerializer(products, many=True)
        return serializer.data
    
     # Cuenta las reseñas por cada calificación 
    def get_poor_review(self, product):
        poor_review_count = product.reviews.filter(rating=1).count()
        return poor_review_count
    
    def get_fair_review(self, product):
        fair_review_count = product.reviews.filter(rating=2).count()
        return fair_review_count
    
    def get_good_review(self, product):
        good_review_count = product.reviews.filter(rating=3).count()
        return good_review_count
    
    def get_very_good_review(self, product):
        very_good_review_count = product.reviews.filter(rating=4).count()
        return very_good_review_count
    
    def get_excellent_review(self, product):
        excellent_review_count = product.reviews.filter(rating=5).count()
        return excellent_review_count


# -------------------------- LISTA DE CATEGORÍAS --------------------------
class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image", "slug"]


# -------------------------- DETALLES DE CATEGORÍA  --------------------------
class CategoryDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)  # Lista los productos relacionados usando un serializer anidado
    class Meta:
        model = Category
        fields = ["id", "name", "image", "products"]


# -------------------------- ITEM DEL CARRITO --------------------------
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True) # Muestra los datos del producto asociado al ítem del carrito (solo lectura)
    sub_total = serializers.SerializerMethodField()   # Campo calculado manualmente (precio * cantidad)

    class Meta:
        model = CartItem 
        fields = ["id", "product", "quantity", "sub_total"]

    # Calcula el subtotal multiplicando precio por cantidad
    def get_sub_total(self, cartitem):
        total = cartitem.product.price * cartitem.quantity 
        return total


# -------------------------- CARRITO --------------------------
class CartSerializer(serializers.ModelSerializer):
    cartitems = CartItemSerializer(read_only=True, many=True)  # Lista de ítems del carrito usando su serializer (solo lectura)
    cart_total = serializers.SerializerMethodField() # Campo calculado manualmente: suma total del carrito
    class Meta:
        model = Cart 
        fields = ["id", "cart_code", "cartitems", "cart_total"]

    # Calcula el total del carrito sumando precio * cantidad de todos los ítems     
    def get_cart_total(self, cart):
        items = cart.cartitems.all()
        total = sum([item.quantity * item.product.price for item in items])
        return total
    
# -------------------------- DETALLES DEL CARRITO --------------------------
class CartStatSerializer(serializers.ModelSerializer):  
    total_quantity = serializers.SerializerMethodField()  # Campo calculado: cantidad total de productos en el carrito
    class Meta:
        model = Cart 
        fields = ["id", "cart_code", "total_quantity"]

    # Suma la cantidad total de todos los ítems del carrito
    def get_total_quantity(self, cart):
        items = cart.cartitems.all()
        total = sum([item.quantity for item in items])
        return total



# -------------------------- LISTA DE DESEADOS --------------------------
class WishlistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # Muestra la información del usuario que agregó el producto (solo lectura)
    product = ProductListSerializer(read_only=True) # Muestra el producto deseado usando su serializer (solo lectura)
    class Meta:
        model = Wishlist 
        fields = ["id", "user", "product", "created"]


# -------------------------- ITEMS DE LA ORDEN --------------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)  # Muestra el producto asociado al ítem de la orden
    class Meta:
        model = OrderItem
        fields = ["id", "quantity", "product"]


# -------------------------- ORDEN --------------------------
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)  # Lista los ítems de la orden (solo lectura, muchos)
    class Meta: 
        model = Order 
        fields = ["id", "stripe_checkout_id", "amount", "items", "status", "created_at"]


# -------------------------- DIRECCION DEL CLIENTE --------------------------
class CustomerAddressSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True) # Muestra los datos del usuario asociado a la dirección
    class Meta:
        model = CustomerAddress
        fields = "__all__"# Incluye todos los campos del modelo en la respuesta


# --------------------------  --------------------------
class SimpleCartSerializer(serializers.ModelSerializer):
    num_of_items = serializers.SerializerMethodField()   # Campo calculado: cantidad total de ítems en el carrito
    class Meta:
        model = Cart 
        fields = ["id", "cart_code", "num_of_items"]

    # Suma la cantidad total de productos en el carrito
    def get_num_of_items(self, cart):
        num_of_items = sum([item.quantity for item in cart.cartitems.all()])
        return num_of_items
