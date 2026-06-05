# Generated manually for adding 'confirmed' status

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0030_sitesettings_admin_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('confirmed', 'Confirmed'),
                    ('paid', 'Paid'),
                    ('cancelled', 'Cancelled')
                ],
                db_index=True,
                default='pending',
                max_length=20
            ),
        ),
    ]
