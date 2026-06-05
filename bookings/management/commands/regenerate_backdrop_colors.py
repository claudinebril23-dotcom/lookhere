from django.core.management.base import BaseCommand
from bookings.models import Backdrop

class Command(BaseCommand):
    help = 'Regenerate colors for all existing backdrops'

    def handle(self, *args, **options):
        backdrops = Backdrop.objects.all()
        updated_count = 0
        
        for backdrop in backdrops:
            old_color = backdrop.color
            # Clear the color to force regeneration
            backdrop.color = ''
            backdrop.save()
            updated_count += 1
            
            self.stdout.write(
                f'Updated "{backdrop.name}": {old_color} -> {backdrop.color}'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} backdrop colors')
        )