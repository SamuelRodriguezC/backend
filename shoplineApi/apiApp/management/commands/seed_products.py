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
            'cámara Digital Robótica': (150.000, 'Electrónica', 'apple-robotic-digital-camera-min.jpg'),
            'Smart Black V9': (450.000, 'Electrónica', 'smart-black-v9-min.jpg'),
            'Camara Sony 4K': (10200.000, 'Electrónica', 'sony-4k-digital-camera-min.jpg'),
            'Video Grabadora': (300.00, 'Electrónica', 'simple-videogragher-set-min.jpg'),
            'Control X-Box': (153.000, 'Electrónica', 'smasung-gaming-pad-min.jpg'),

            # Ropa
            'Camisa Azul Cuadros': (35.000, 'Ropa', 'apple-packed-tshirt-min.jpg'),
            'Baggy Jeans': (59.000, 'Ropa', 'baggy-sized-jeans-min.jpg'),
            'Chaqueta blanca Algodón': (120.000, 'Ropa', 'milky-jacket-min.jpg'),
            'Gucci Buzo Azul': (450.500, 'Ropa', 'gucci-purple-sweater-min.jpg'),
            'Vestido Verde para Mujer': (80.900, 'Ropa', 'female-blue-dress-min.jpg'),
            'Abrigo Verde para Mujer': (80.900, 'Ropa', 'female-green-jacket-min.jpg'),
            'Chaqueta Tommy hifliger': (452.000, 'Ropa', 'tommyhilfiger-sweaters-min.jpg'),
            'Chaqueta de Cuadros Azul': (150.000, 'Ropa', 'gucci-clothing-set-min.jpg'),

            # Libros
            'Libros Desarrollo Personal': (49.700, 'Libros', 'elon-recommended-books-min.jpg'),
            'Libros de Historia': (39.000, 'Libros', 'jeff-recommed-books-min.jpg'),
            'Libros Filosofía': (45.300, 'Libros', 'trump-recommended-books-min.jpg'),
            'Libros Sociología': (60.100, 'Libros', 'lord-of-the-rings-min.jpg'),
            'Libros Fisica': (475.000, 'Libros', 'hooked-book-min.jpg'),

            # Comida
            'Fresas Importadas': (5.700, 'Comida', 'american-strawberry-min.jpg'),
            'Pastel de Chocolate': (15.300, 'Comida', 'chocolate-baked-cake-min.jpg'),
            'Pastel de Fresas con chocolate': (18.000, 'Comida', 'strawberry-chocolate-cake-min.jpg'),
            'Macarrones': (8.400, 'Comida', 'coloured-macaroons-min.jpg'),
            'Macarroes Pasta': (7.750, 'Comida', 'fried-macaroons-min.jpg'),
            'Spaghetti': (12.400, 'Comida', 'fried-spaghetti-min.jpg'),
            'Pescado Frito con Vegetales': (22.400, 'Comida', 'fried-fish-with-vegetable-min.jpg'),
            'Papas Fritas con Hamburguesa': (9.99, 'Comida', 'fired-chips-with-burger-min.jpg'),

            # Juguetes
            'Remolque': (250.400, 'Juguetes', 'amoured_caterpillar-trailer-min.jpg'),
            'Autobús de juguete Bumble B': (35.900, 'Juguetes', 'bumble-b-toy-bus-min.jpg'),
            'Vehículos de juguete': (45.300, 'Juguetes', 'toy-trailer-vehicles-min.jpg'),
            'Camioneta Tundra Juguete': (45.880, 'Juguetes', 'toy-tundra-car-min.jpg'),
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
                    product.image.name = f'product_img/{image_filename}'

                product.save()
                self.stdout.write(self.style.SUCCESS(f'Producto "{name}" creado en la categoría "{category_name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Producto "{name}" ya existe'))
