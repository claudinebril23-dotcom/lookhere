from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0038_remove_package_tier'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='enable_bookings',
            field=models.BooleanField(default=True, help_text='Enable or disable the booking system for customers'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='max_daily_bookings',
            field=models.IntegerField(default=0, help_text='Maximum number of bookings allowed per day (0 = unlimited)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='booking_advance_days',
            field=models.IntegerField(default=30, help_text='How many days in advance customers can book (e.g., 30 = up to 30 days from today)'),
        ),
    ]
