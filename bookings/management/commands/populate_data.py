from django.core.management.base import BaseCommand
from bookings.models import Addon, Backdrop

class Command(BaseCommand):
    help = 'Populate database with add-ons and backdrops'

    def handle(self, *args, **options):
        # Clear existing data
        Addon.objects.all().delete()
        Backdrop.objects.all().delete()
        
        # Add-ons
        addons = [
            {'name': 'Additional Pax', 'price': 200, 'description': 'Extra person for the photoshoot'},
            {'name': 'Additional Pet', 'price': 100, 'description': 'Extra pet for the photoshoot'},
            {'name': '1 pc 4R Print', 'price': 65, 'description': '1 piece 4R size print'},
            {'name': '1 pc 3R Print', 'price': 100, 'description': '1 piece 3R size print'},
            {'name': '1pc 4R + Frame', 'price': 380, 'description': '1 piece 4R print with frame (upon frame availability)'},
            {'name': '1pc 8R + Frame', 'price': 500, 'description': '1 piece 8R print with frame (upon frame availability)'},
            {'name': '1 pc 8R Print', 'price': 180, 'description': '1 piece 8R size print'},
            {'name': 'Black Toga with cap and hood', 'price': 150, 'description': 'Max of 2 sets, per set'},
            {'name': '2 pcs Photocard Print', 'price': 100, 'description': '2 pieces photocard prints'},
            {'name': '4 pcs Cute Size Print', 'price': 120, 'description': '4 pieces cute size prints'},
            {'name': '2 pcs Strip Print', 'price': 150, 'description': '2 pieces strip prints'},
            {'name': '2 pcs Special Film Strip Print', 'price': 180, 'description': '2 pieces special film strip prints'},
            {'name': 'Additional Backdrop / plain color', 'price': 100, 'description': 'Additional plain color backdrop'},
            {'name': 'Floor Extension / backdrop', 'price': 300, 'description': 'Floor extension for backdrop'},
            {'name': 'Spotlight Setup', 'price': 300, 'description': 'Professional spotlight setup'},
            {'name': 'Techno-Gradient light Setup', 'price': 300, 'description': 'Techno-gradient lighting setup'},
            {'name': 'Red Curtain Backdrop', 'price': 200, 'description': 'Red curtain backdrop without floor extension'},
            {'name': 'All Digital Copies', 'price': 300, 'description': 'All digital copies (PHP 200 only for Solo and Spotlight package)'},
            {'name': 'Additional Self-shoot Enhanced Photo (5 Photos)', 'price': 200, 'description': 'Additional enhanced photos, succeeding is PHP40/photo'},
        ]
        
        for addon_data in addons:
            Addon.objects.create(**addon_data)
        
        # Plain Backdrops
        plain_backdrops = [
            {'name': 'Butter Cream', 'type': 'solid', 'color': '#F5E6A3'},
            {'name': 'Snow White', 'type': 'solid', 'color': '#FFFFFF'},
            {'name': 'Cocoa Brown (Available until Feb 28)', 'type': 'solid', 'color': '#8B4513'},
            {'name': 'Arc Gray', 'type': 'solid', 'color': '#708090'},
            {'name': 'Red', 'type': 'solid', 'color': '#DC143C'},
            {'name': 'Blue Jay', 'type': 'solid', 'color': '#4682B4'},
            {'name': 'Gray (Available by March 1)', 'type': 'solid', 'color': '#808080'},
            {'name': 'Purple', 'type': 'solid', 'color': '#800080'},
        ]
        
        # Creative Backdrops
        creative_backdrops = [
            {'name': 'Floral Garden', 'type': 'theme', 'color': '#90EE90'},
            {'name': 'White Door', 'type': 'theme', 'color': '#F8F8FF'},
            {'name': 'Red Theater Curtain w/ Floor extension', 'type': 'theme', 'color': '#8B0000'},
        ]
        
        for backdrop_data in plain_backdrops + creative_backdrops:
            Backdrop.objects.create(**backdrop_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(addons)} add-ons and {len(plain_backdrops + creative_backdrops)} backdrops')
        )