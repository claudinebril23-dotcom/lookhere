from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(f"Email Configuration:")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        try:
            send_mail(
                'Test Email from Look Here Studio',
                'This is a test email to verify your email configuration is working correctly.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Test email sent successfully to {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send test email: {e}'))
