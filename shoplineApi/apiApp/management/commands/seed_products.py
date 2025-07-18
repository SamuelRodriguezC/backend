from django.core.management.base import BaseCommand
from apiApp.models import Product, Category
from django.core.files import File
from django.utils.text import slugify
import os
import random

class Command(BaseCommand):
    help = 'Seed products with images and categories'

    def handle(self, *args, **kwargs):
        # Diccionario: nombre producto => (precio, categoría, imagen)
        products = {
            # Electrónica
            'Apple Robotic Digital Camera': (150.000, 'Electrónica', 'apple-robotic-digital-camera-min.jpg'),
            'Smart Black V9': (450.000, 'Electrónica', 'smart-black-v9-min.jpg'),
            'Sony 4K Digital Camera': (10200.000, 'Electrónica', 'sony-4k-digital-camera-min.jpg'),
            'Samsung Gaming Pad': (300.00, 'Electrónica', 'samsung-gaming-pad-min.jpg'),

            # Ropa
            'Apple Packed T-Shirt': (35.000, 'Ropa', 'apple-packed-tshirt-min.jpg'),
            'Baggy Sized Jeans': (59.000, 'Ropa', 'baggy-sized-jeans-min.jpg'),
            'Milky Jacket': (120.000, 'Ropa', 'milky-jacket-min.jpg'),
            'Gucci Purple Sweater': (450.500, 'Ropa', 'gucci-purple-sweater-min.jpg'),
            'Female Blue Dress': (80.900, 'Ropa', 'female-blue-dress-min.jpg'),

            # Libros
            'Elon Recommended Books': (49.700, 'Libros', 'elon-recommended-books-min.jpg'),
            'Jeff Recommended Books': (39.000, 'Libros', 'jeff-recommed-books-min.jpg'),
            'Trump Recommended Books': (45.300, 'Libros', 'trump-recommended-books-min.jpg'),
            'Lord of the Rings': (60.100, 'Libros', 'lord-of-the-rings-min.jpg'),

            # Comida
            'American Strawberry': (5.700, 'Comida', 'american-strawberry-min.jpg'),
            'Chocolate Baked Cake': (15.300, 'Comida', 'chocolate-baked-cake-min.jpg'),
            'Strawberry Chocolate Cake': (18.000, 'Comida', 'strawberry-chocolate-cake-min.jpg'),
            'Coloured Macaroons': (8.400, 'Comida', 'coloured-macaroons-min.jpg'),
            'Fried Macaroons': (7.750, 'Comida', 'fried-macaroons-min.jpg'),
            'Fried Spaghetti': (12.400, 'Comida', 'fried-spaghetti-min.jpg'),
            'Fried Fish with Vegetable': (22.400, 'Comida', 'fried-fish-with-vegetable-min.jpg'),
            'Fried Chips with Burger': (9.99, 'Comida', 'fried-chips-with-burger-min.jpg'),

            # Juguetes
            'Amoured Caterpillar Trailer': (250.400, 'Juguetes', 'amoured_caterpillar-trailer-min.jpg'),
            'Bumble B Toy Bus': (35.900, 'Juguetes', 'bumble-b-toy-bus-min.jpg'),
            'Toy Trailer Vehicles': (45.300, 'Juguetes', 'toy-trailer-vehicles-min.jpg'),
        }

        image_base_path = os.path.join('media', 'product_img')

        for name, (price, category_name, image_filename) in products.items():
            category = Category.objects.filter(name=category_name).first()

            if not category:
                self.stdout.write(self.style.WARNING(f'Categoría "{category_name}" no encontrada para el producto "{name}"'))
                continue

            if not Product.objects.filter(name=name).exists():
                product = Product(
                    name=name,
                    description = f'El {name} es un producto diseñado pensando en la calidad, el rendimiento y la satisfacción del cliente. Fabricado con materiales de alta durabilidad, ofrece una experiencia única gracias a su funcionalidad y diseño moderno. Ya sea para uso diario o profesional, el {name} cumple con los más altos estándares, brindando confianza y versatilidad en cada uso. Su excelente relación calidad-precio lo convierte en una opción ideal para quienes buscan lo mejor sin comprometer su presupuesto.',
                    price=price,
                    featured=random.choice([True, False]),
                    category=category,
                    slug=slugify(name)
                )

                image_path = os.path.join(image_base_path, image_filename)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img_file:
                        product.image.save(image_filename, File(img_file), save=False)

                product.save()
                self.stdout.write(self.style.SUCCESS(f'Producto "{name}" creado en la categoría "{category_name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Producto "{name}" ya existe'))
