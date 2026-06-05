import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'narrativestudio.settings')
django.setup()

from bookings.models import CreativePackage

packages = [
    {'name': 'Neon Lights'},
    {'name': 'Vintage Film'},
    {'name': 'Tropical Paradise'},
]

for pkg in packages:
    cp, created = CreativePackage.objects.get_or_create(
        name=pkg['name']
    )
    if created:
        print(f"Created: {cp.name}")
    else:
        print(f"Already exists: {cp.name}")

print("\nAll Creative Packages:")
for cp in CreativePackage.objects.all():
    print(f"  {cp.name}")
