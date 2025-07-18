# Importa la clase base para crear comandos personalizados
from django.core.management.base import BaseCommand
# Importa el modelo Category al que vamos a hacer el seed
from apiApp.models import Category
# Importa el manejador de archivos de Django para guardar imágenes
from django.core.files import File
# Para generar el slug automáticamente a partir del nombre
from django.utils.text import slugify
import os  # Para trabajar con rutas de archivos

# Define el comando personalizado heredando de BaseCommand
class Command(BaseCommand):
    help = 'Seed categories with images'  # Mensaje de ayuda que aparece al usar --help

    # Función que se ejecuta al correr el comando
    def handle(self, *args, **kwargs):
        # Diccionario con categorías (clave = nombre, valor = nombre del archivo de imagen)
        categories = {
            'Electrónica': 'electronics.svg',
            'Ropa': 'clothing.svg',
            'Libros': 'books.svg',
            'Comida': 'food.svg',
            'Juguetes': 'toy.svg',
        }

        # Ruta base donde están las imágenes dentro de la carpeta del proyecto
        image_base_path = os.path.join('media', 'category_img')

        for name, image_filename in categories.items():
            if not Category.objects.filter(name=name).exists():
                category = Category(name=name, slug=slugify(name))

                image_path = os.path.join(image_base_path, image_filename)
                if os.path.exists(image_path):
                    category.image.name = f'category_img/{image_filename}'
                else:
                    self.stdout.write(self.style.WARNING(f'Imagen "{image_filename}" no encontrada para la categoría "{name}"'))

                category.save()
                self.stdout.write(self.style.SUCCESS(f'Categoría "{name}" creada'))
            else:
                self.stdout.write(self.style.WARNING(f'Categoría "{name}" ya existe'))