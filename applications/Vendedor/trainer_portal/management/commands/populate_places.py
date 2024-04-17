from django.core.management.base import BaseCommand
from trainer_portal.models import LugarEstadio

class Command(BaseCommand):
    help = 'Populate database with stadium places'

    def handle(self, *args, **kwargs):
        # Loop through rows A-E
        for linha in ['A', 'B', 'C', 'D', 'E']:
            # Loop through columns 1-10
            for coluna in range(1, 11):
                lugar, created = LugarEstadio.objects.get_or_create(
                    linha=linha,
                    coluna=str(coluna),
                    defaults={'disponivel': True}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Criado lugar: {lugar}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Lugar já existe: {lugar}'))
