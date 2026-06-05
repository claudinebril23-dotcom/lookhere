from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0019_add_payment_method_column'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hero_background_image', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='hero/',
                    help_text='Upload the homepage hero background image (recommended: 1920×1080px or larger)'
                )),
                ('hero_overlay_opacity', models.FloatField(
                    default=0.45,
                    help_text='Dark overlay opacity over the hero image (0.0 = no overlay, 1.0 = fully black). Recommended: 0.3–0.7'
                )),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Site Settings',
                'verbose_name_plural': 'Site Settings',
            },
        ),
    ]
