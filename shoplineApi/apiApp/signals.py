from django.db.models.signals import post_save, post_delete 
from django.dispatch import receiver
from django.db.models import Avg

from apiApp.models import ProductRating, Review


# signals.py MANEJAR EVENTOS AUTOMÁTICOS 



# Esta función se ejecuta después de guardar una reseña
@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    product = instance.product  # Obtiene el producto asociado a la reseña recién guardada
    reviews = product.reviews.all() # Obtiene todas las reseñas de ese producto
    total_reviews = reviews.count() # Cuenta cuántas reseñas tiene el producto

    # Calcula el promedio de calificaciones (si no hay reseñas, el promedio será 0.0)
    review_average = reviews.aggregate(Avg("rating"))["rating__avg"] or 0.0



    # Busca o crea un objeto ProductRating asociado al producto
    product_rating, created = ProductRating.objects.get_or_create(product=product)

    # Actualiza el promedio y el número total de reseñas
    product_rating.average_rating = review_average 
    product_rating.total_reviews = total_reviews 
    product_rating.save()# Guarda los cambios



# Esta función se ejecuta después de eliminar una reseña
@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    product = instance.product  # Obtiene el producto asociado a la reseña que fue eliminada
    reviews = product.reviews.all()  # Obtiene las reseñas restantes del producto
    total_reviews = reviews.count() # Cuenta las reseñas restantes

    # Recalcula el promedio de calificaciones
    review_average = reviews.aggregate(Avg("rating"))["rating__avg"] or 0.0

    # Busca o crea el objeto ProductRating correspondiente
    product_rating, created = ProductRating.objects.get_or_create(product=product)

    # Actualiza los datos del promedio y total de reseñas
    product_rating.average_rating = review_average 
    product_rating.total_reviews = total_reviews 
    product_rating.save() 