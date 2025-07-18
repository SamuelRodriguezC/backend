from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Ejecuta todos los seeders (categorías, productos, etc.)'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.NOTICE("Sembrando categorías..."))
            call_command('seed_categories')

            self.stdout.write(self.style.NOTICE("Sembrando productos..."))
            call_command('seed_products')


            self.stdout.write(self.style.SUCCESS(" Todos los seeders fueron ejecutados correctamente."))
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"Error ejecutando seeders: {e}"))
