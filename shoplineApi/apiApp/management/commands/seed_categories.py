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

        # Itera sobre cada categoría y su imagen asociada
        for name, image_filename in categories.items():
            # Si la categoría no existe todavía en la base de datos...
            if not Category.objects.filter(name=name).exists():
                # Crea la categoría con su nombre y slug generado automáticamente
                category = Category(name=name, slug=slugify(name))

                # Construye la ruta completa del archivo de imagen
                image_path = os.path.join(image_base_path, image_filename)

                # Si el archivo existe en la ruta especificada...
                if os.path.exists(image_path):
                    # Abre el archivo en modo binario de lectura
                    with open(image_path, 'rb') as img_file:
                        # Asigna el archivo al campo image del modelo sin guardar aún en la DB
                        category.image.save(image_filename, File(img_file), save=False)

                # Guarda la categoría (ya sea con o sin imagen)
                category.save()
                
                # Mensaje de éxito en la terminal
                self.stdout.write(self.style.SUCCESS(f'Categoría "{name}" creada con imagen "{image_filename}"'))
            else:
                # Si la categoría ya existe, muestra una advertencia
                self.stdout.write(self.style.WARNING(f'Categoría "{name}" ya existe'))
