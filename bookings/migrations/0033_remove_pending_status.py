# Generated manually

from django.db import migrations, models


def update_pending_to_confirmed(apps, schema_editor):
    """Update all existing 'pending' bookings to 'confirmed'"""
    Booking = apps.get_model('bookings', 'Booking')
    Booking.objects.filter(status='pending').update(status='confirmed')


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0032_add_performance_indexes'),
    ]

    operations = [
        # First, update all pending bookings to confirmed
        migrations.RunPython(update_pending_to_confirmed, migrations.RunPython.noop),
        
        # Then, alter the field to remove 'pending' from choices and change default
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[
                    ('confirmed', 'Confirmed'),
                    ('paid', 'Paid'),
                    ('cancelled', 'Cancelled')
                ],
                db_index=True,
                default='confirmed',
                max_length=20
            ),
        ),
    ]
