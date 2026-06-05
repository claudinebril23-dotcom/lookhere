# Generated migration to remove daily_booking_limit column from database

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0009_booking_payment_proof_alter_booking_status'),
    ]

    operations = [
        migrations.RunSQL(
            sql="",
            reverse_sql="",
        ),
    ]
