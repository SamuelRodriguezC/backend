import stripe 
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Category, CustomerAddress, Order, OrderItem, Product, Review, Wishlist
from .serializers import CartItemSerializer, CartSerializer, CategoryDetailSerializer, CategoryListSerializer, CustomerAddressSerializer, OrderSerializer, ProductListSerializer, ProductDetailSerializer, ReviewSerializer, SimpleCartSerializer, UserSerializer, WishlistSerializer


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


# Las views son funciones o clases que manejan la lógica de una solicitud HTTP.
# Reciben una petición del cliente (por ejemplo, desde un navegador o una API) y devuelven una respuesta (HTML, JSON, redirección, etc.).





# Variables para pagos en líneas
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.WEBHOOK_SECRET

# Asignar a la variable el modelo de usuario activo en el proyecto (settings.py)
User = get_user_model()

# -------------------------------------------- LISTA DE PRODUCTOS --------------------------------------------
@api_view(['GET'])
def product_list(request):
    products = Product.objects.filter(featured=True) #Obtener todos los objetos donde el campo featured = True 
    serializer = ProductListSerializer(products, many=True) #Convertir el resultado de la busqueda anterior en JSON
    return Response(serializer.data) #Devolver los datos filtrados y serializados

# Ejemplo de la petición desde el front (djago se encarga de pasar el parametro request)
# const response = await api.get("product_list")
# return response.data


# -------------------------------------------- DETALLES DE PRODUCTO --------------------------------------------
@api_view(["GET"])
def product_detail(request, slug): # Recibe el request(automático) y el slug (enviado desde el front)
    product = Product.objects.get(slug=slug) # Obtiene un producto con ese slug 
    serializer = ProductDetailSerializer(product) # Convierte el producto a JSON
    return Response(serializer.data) # Devuelve los taddos serializados del producto
# Ejemplo de la petición desde el front:
# const response = await api.get(`product_detail/${slug}`)
# return response.data


# -------------------------------------------- LISTA DE CATEGORÍAS --------------------------------------------
@api_view(["GET"])
def category_list(request):
    categories = Category.objects.all() #Obtener todos los objetos de tipo category
    serializer = CategoryListSerializer(categories, many=True) #Serializar los objetos
    return Response(serializer.data) # Retornar categorias serializadas

# -------------------------------------------- DETALLES DE CATEGORÍA --------------------------------------------
@api_view(["GET"])
def category_detail(request, slug): # Recibir el slug 
    category = Category.objects.get(slug=slug) # Buscar categoría con el slug
    serializer = CategoryDetailSerializer(category) #Serializa categoría
    return Response(serializer.data) #Dvolder detalles de categoria serializado

# -------------------------------------------- AÑADIR AL CARRITO --------------------------------------------
@api_view(["POST"])
def add_to_cart(request):

    # Extraer los valores enviados en el cuerpo de la solicitud POST (request) desde el front
    cart_code = request.data.get("cart_code")
    product_id = request.data.get("product_id")

    # Busca o crea un carrito con el código proporcionado 
    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product = Product.objects.get(id=product_id) # Obtiene el producto por el id 

    # Busca o crea una relación entre el producto y el carrito en la tabla intermedia 
    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart) 

    # Establece la cantidad del producto que se va a añadir al carrito = default 1
    cartitem.quantity = 1 

    # Guardar el producto en la base de datos (id, product, quantity, cart)
    cartitem.save() 

    serializer = CartSerializer(cart) # Serializar el carrito
    return Response(serializer.data) # Devolver el carrito serializado

# -------------------------------------------- ACTUALIZAR CANTIDAD DE PRODUCTOS EN EL CARRITO ------------------------------
@api_view(['PUT'])
def update_cartitem_quantity(request):

    # Extraer los valores enviados en el cuerpo de la solicitud PUT (request) desde el front
    cartitem_id = request.data.get("item_id")
    quantity = request.data.get("quantity")

    quantity = int(quantity) # Convertir la cantidad a entero

    cartitem = CartItem.objects.get(id=cartitem_id) # Obtener el objeto de carrito con el id correspondiente
    cartitem.quantity = quantity # Setear la cantidad a la cantidad recibida desde el front
    cartitem.save() # Guardar en la base de datos

    serializer = CartItemSerializer(cartitem) #Serializar el item actualizado
    return Response({"data": serializer.data, "message": "Cartitem updated successfully!"}) # Devolver respuesta


# -------------------------------------------- AÑADIR RESEÑA --------------------------------------------
@api_view(["POST"])
def add_review(request):
    
    # Extraer los valores enviados en el cuerpo de la solicitud POST (request) desde el front
    product_id = request.data.get("product_id")
    email = request.data.get("email")
    rating = request.data.get("rating")
    review_text = request.data.get("review")

    # Obtener el producto que tiene el id 
    product = Product.objects.get(id=product_id)
    # Obtener el usuario con el email
    user = User.objects.get(email=email)

    # Si existe la review donde el esté el producto y el usuario 
    if Review.objects.filter(product=product, user=user).exists():
        # Retornar mensaje de error que indica que el usuario ya tiene una reseña en ese producto
        return Response({"error": "You already dropped a review for this product"}, status=400)

    # Crear reseña con los ddatos enviados desde el front
    review  = Review.objects.create(product=product, user=user, rating=rating, review=review_text)
    # Serializar la reseña recién creada
    serializer = ReviewSerializer(review)
    # Responser con la reseña serializada
    return Response(serializer.data)


# -------------------------------------------- ACTUALIZAR RESEÑA --------------------------------------------
@api_view(['PUT'])
def update_review(request, pk): #Solicitar el id o llave primaria de la reseña

    # Obtener los datos enviados en el cuerpo de la solicitud PUT enviada desde el front
    review = Review.objects.get(id=pk) 
    rating = request.data.get("rating")
    review_text = request.data.get("review")

    # Al objeto review actualizar el campo rating por el rating enviado en la solicitud
    review.rating = rating 
    # Actualizar el campo review por el enviado en la solicitud
    review.review = review_text
    # Guardar en la base de datos
    review.save()

    # Serializar la reseña actualizada 
    serializer = ReviewSerializer(review)
    # Retornar la reseña actualizada y serializada
    return Response(serializer.data)


# -------------------------------------------- ELIMINAR RESEÑA  --------------------------------------------
@api_view(['DELETE'])
def delete_review(request, pk): # solicitar la llave primaria o el id de la reseña
    review = Review.objects.get(id=pk) 

    # Elimninar de la base de datos la reseña
    review.delete()

    # Mostrar mensaje de exito en la operación 
    return Response("Review deleted successfully!", status=200)


# -------------------------------------------- ELIMINAR PRODUCTO DEL CARRITO --------------------------------------------
@api_view(['DELETE'])
def delete_cartitem(request, pk): # Solicitar el id del producto del carrito

    # Obtener el item del carrito con ese id
    cartitem = CartItem.objects.get(id=pk) 

    # Eliminar el producto del carrito
    cartitem.delete()

    # Mostrar mensaje de exito
    return Response({"message": "Cartitem deleted successfully!"}, status=200)


# -------------------------------------------- AÑADIR A LISTA DE DESEOS --------------------------------------------
@api_view(['POST'])
def add_to_wishlist(request):

    # Extraer datos del cuerpo de la solicitud POST
    email = request.data.get("email")
    product_id = request.data.get("product_id")

    # Obtener el objeto usuario que contiene el email proporcionado
    user = User.objects.get(email=email)
    # Obtener el objeto producto que tiene el id proporcionado
    product = Product.objects.get(id=product_id) 

    # Buscar en la lista de deseados un objeto con el usuario y el producto proporcionados
    wishlist = Wishlist.objects.filter(user=user, product=product)

    # Si la lista de deseados existe
    if wishlist:
        # Eliminar de la base de datos
        wishlist.delete()
        # Mostrar mensaje de exito en la eliminación 
        return Response({"message": "Wishlist deleted successfully", "action": "deleted"}, status=200)

    # Crear una nueva lista de deseados usando el usuario y producto proporcionados
    new_wishlist = Wishlist.objects.create(user=user, product=product)

    # Serializar la lista de deseos
    serializer = WishlistSerializer(new_wishlist)

    # Retornar la lista de deseados e informar que ha sido creada correctamente
    return Response({"wishlist": serializer.data, "action": "created"}, status=201)


# -------------------------------------------- BUSCAR PRODUCTOS --------------------------------------------
@api_view(['GET'])
def product_search(request):
    # Obtener la datos del cuerpo de la solicitud get
    query = request.query_params.get("query") 

    # Si no hay texto de busqueda
    if not query:
        # Mostrar mensaje de error
        return Response("No query provided", status=400)
    
    # Buscar productos que tengan el nombre, descripción o categoría igual al filtro de busqueda proporcionado
    products = Product.objects.filter(Q(name__icontains=query) | 
                                      Q(description__icontains=query) |
                                       Q(category__name__icontains=query) )
    
    # Serializar los productos obtenidos luego del filtro
    serializer = ProductListSerializer(products, many=True)

    # Retornar los productos serializados
    return Response(serializer.data)
    



# --------------------------------------------  --------------------------------------------
@api_view(['POST'])
def create_checkout_session(request):
    cart_code = request.data.get("cart_code") # Se obtiene el código del carrito del frontend
    email = request.data.get("email") # Se obtiene el correo del cliente
    cart = Cart.objects.get(cart_code=cart_code) # Se busca el carrito en la base de datos
    try:
        # Se crea una sesión de pago con Stripe
        checkout_session = stripe.checkout.Session.create(
            customer_email= email,  # Correo del cliente
            payment_method_types=['card'],  # Solo se aceptan pagos con tarjeta

            # Se construye la lista de productos a cobrar
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item.product.name},
                        'unit_amount': int(item.product.price * 100),  # Monto en centavos
                    },
                    'quantity': item.quantity,
                }
                for item in cart.cartitems.all() # Se recorre cada ítem del carrito
            ] + [
                # Se añade un ítem adicional con un cargo de $5 (impuesto o tarifa)
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'VAT Fee'},
                        'unit_amount': 500,  # $5 in cents
                    },
                    'quantity': 1,
                }
            ],

            mode='payment', # Modo de pago (pago único)

            # URLs a las que redirige Stripe después del pago
            # success_url="https://nextshoppit.vercel.app/success",
            # cancel_url="https://nextshoppit.vercel.app/cancel",

            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/failed",
            metadata = {"cart_code": cart_code} # Información adicional útil en el webhook
        )
        return Response({'data': checkout_session})  # Se retorna la sesión al frontend
    except Exception as e: 
        return Response({'error': str(e)}, status=400) # Error manejado y enviado como respuesta




@csrf_exempt
def my_webhook_view(request):
    payload = request.body  # Se obtiene el contenido crudo de la petición
    sig_header = request.META['HTTP_STRIPE_SIGNATURE'] # Firma enviada por Stripe
    event = None

    try:
        # Verifica que la firma del webhook sea válida
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # El contenido no es válido (no es un JSON, etc.)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # La firma no coincide, puede ser un intento de fraude
        return HttpResponse(status=400)

    # Si el pago fue exitoso (sincrónico o asincrónico)
    if (
        event['type'] == 'checkout.session.completed'
        or event['type'] == 'checkout.session.async_payment_succeeded'
    ):
        session = event['data']['object']  # Si el pago fue exitoso (sincrónico o asincrónico)
        cart_code = session.get("metadata", {}).get("cart_code") # Se extrae el cart_code

        fulfill_checkout(session, cart_code)  # Se llama la función que genera la orden


    return HttpResponse(status=200) # Se responde a Stripe que todo está bien



def fulfill_checkout(session, cart_code):
    # Crea un nuevo pedido en la base de datos con los datos recibidos de Stripe
    order = Order.objects.create(stripe_checkout_id=session["id"],
        amount=session["amount_total"],
        currency=session["currency"],
        customer_email=session["customer_email"],
        status="Paid") # Se marca como pagado
    

    print(session)

    cart = Cart.objects.get(cart_code=cart_code) # Se obtiene el carrito
    cartitems = cart.cartitems.all() # Se obtienen los productos del carrito

    # Se crea un OrderItem para cada producto en el carrito
    for item in cartitems:
        orderitem = OrderItem.objects.create(order=order, product=item.product, 
                                             quantity=item.quantity)
    
    cart.delete() # Se elimina el carrito porque ya se procesó el pedido






# -------------------------------------------- CREAR USUARIO --------------------------------------------
@api_view(["POST"])
def create_user(request):

    # Extraer datos del cuerpo de la solicitud POST enviada desde el front
    username = request.data.get("username")
    email = request.data.get("email")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    profile_picture_url = request.data.get("profile_picture_url")

    # Crear el usuario con los datos proporcionados
    new_user = User.objects.create(username=username, email=email,
                                       first_name=first_name, last_name=last_name, profile_picture_url=profile_picture_url)
    
    # Serializar el usuario creado
    serializer = UserSerializer(new_user)

    # Retornar el usuario serializado 
    return Response(serializer.data)


# -------------------------------------------- BUSCAR USUARIO EXISTENTE --------------------------------------------
@api_view(["GET"])
def existing_user(request, email): #Solicitrar el email del usuario a buscar 
    try:
        # Buscar el objeto usuario con el email proporcionado
        User.objects.get(email=email)
        # Si se encuentrar responder: 
        return Response({"exists": True}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # Si el usuario no existe: 
        return Response({"exists": False}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------------------- OBTENER ORDENES --------------------------------------------
@api_view(['GET'])
def get_orders(request):
    # Obtener datos del cuerpo de la solicitud POST
    email = request.query_params.get("email")

    # Buscar ordenes donde el campo customer_email sea igual al enviado en la solicitud
    orders = Order.objects.filter(customer_email=email)
    # Serializar las ordenes obtenidas en el filtro
    serializer = OrderSerializer(orders, many=True)

    # Responder son las ordenes encontradas serializadas
    return Response(serializer.data)


# -------------------------------------------- AÑADIR DIRECCIÓN  --------------------------------------------
@api_view(["POST"])
def add_address(request):

    # Obtener datos del cuerpo de la solicitud
    email = request.data.get("email")
    street = request.data.get("street")
    city = request.data.get("city")
    state = request.data.get("state")
    phone = request.data.get("phone")

    if not email:
        return Response({"error": "Email is required"}, status=400)
    
    # Buscar usuario con el email proporcionado
    customer = User.objects.get(email=email)

    # Crear la dirección para el usuario 
    address, created = CustomerAddress.objects.get_or_create(
        customer=customer)
    address.email = email 
    address.street = street 
    address.city = city 
    address.state = state
    address.phone = phone 

    # Guardar en la base de datos
    address.save()
    
    # Serializar la dirección de usuario
    serializer = CustomerAddressSerializer(address)

    # Retornar la dirección serializada
    return Response(serializer.data)


# --------------------------------------------  --------------------------------------------
@api_view(["GET"])
def get_address(request):

    # Obtener el email del cuerpo de la solicitud
    email = request.query_params.get("email") 

    # Buscar dirección que contenga el email proporcionado
    address = CustomerAddress.objects.filter(customer__email=email)

    
    if address.exists():
        # Obtener la ultima dirección creada (guiandose por el id)
        address = address.last()
        # Serializar la dirección 
        serializer = CustomerAddressSerializer(address)
        # Retornar la dirección serializada
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Si no hay una dirección con ese corrreo informar el error
    return Response({"error": "Address not found"}, status=200)


# -------------------------------------------- LISTA DE DESEOS DE UN USUARIO --------------------------------------------
@api_view(["GET"])
def my_wishlists(request):

    # Obtener el email del cuerpo de la solicitud
    email = request.query_params.get("email")

    # Buscar lista de deseos con el email proporcionado
    wishlists = Wishlist.objects.filter(user__email=email)
    
    # Serializar la/s lista/s de deseos
    serializer = WishlistSerializer(wishlists, many=True)

    # Retornar la/s lista/s de deseos
    return Response(serializer.data)


# -------------------------------------------- PRODUCTOS DE LA LISTA DE DESEOS --------------------------------------------
@api_view(["GET"])
def product_in_wishlist(request):

    # Obtener datos del cuerpo de la solicitud 
    email = request.query_params.get("email")
    product_id = request.query_params.get("product_id")

    # Si hay una lista de deseos con el producto y email proporcionados 
    if Wishlist.objects.filter(product__id=product_id, user__email=email).exists():
        # Informar que el producto está en la lista de deseos
        return Response({"product_in_wishlist": True})
    
    # Si no se encuentra retornar false
    return Response({"product_in_wishlist": False})


# -------------------------------------------- OBTENER EL CARRITO --------------------------------------------
@api_view(['GET'])
def get_cart(request, cart_code): #solicitar el codigo del carrito

    # Buscar carrito el primer carrito que conicida con el codigo proporcionado
    cart = Cart.objects.filter(cart_code=cart_code).first()
    
    # Si se encuentra 
    if cart:
        # Serializar el carrito obtenido
        serializer = CartSerializer(cart)
        # Retornar el carrito serializado
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Informar que el carrito con el codigo proporcionado no existe
    return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------------------- OBTENER EL STAT DEL CARRITO --------------------------------------------
@api_view(['GET'])
def get_cart_stat(request):

    # Obtener el codigo de carrito desde el cuerpo de la solicitud 
    cart_code = request.query_params.get("cart_code")

    # Buscar el primer carrito que contenga el codigo proporcionado
    cart = Cart.objects.filter(cart_code=cart_code).first()

    # si existe 
    if cart:
        # Serializar el carrito obtenido
        serializer = SimpleCartSerializer(cart)

        # Retornar el carrito serializado
        return Response(serializer.data)
    
    # Informar que no ha encontrado el carrito con el codigo proporcionado
    return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------------------- PRODUCTO EN EL CARRITO --------------------------------------------
@api_view(['GET'])
def product_in_cart(request):

    # Obtener los datos del cuerpo de la solicitud 
    cart_code = request.query_params.get("cart_code")
    product_id = request.query_params.get("product_id")
    
    # Obtener el primer carrito con el codigo proporcionado
    cart = Cart.objects.filter(cart_code=cart_code).first()

    # Obtener el producto con el id proporcionado
    product = Product.objects.get(id=product_id)

    # verificar existencia el cartItem que conincida con el carrito y producto 
    product_exists_in_cart = CartItem.objects.filter(cart=cart, product=product).exists() #True or False

    return Response({'product_in_cart': product_exists_in_cart})



@api_view(['GET'])
def featured_products_limit(request):
    limit = request.GET.get('limit')  # Obtiene el parámetro "limit" de la URL

    products = Product.objects.filter(featured=True)

    # Si el parámetro "limit" fue proporcionado, aplicar límite
    if limit is not None:
        try:
            limit = int(limit)
            products = products[:limit]
        except ValueError:
            pass  # Si no es un entero válido, ignora y devuelve todos

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)