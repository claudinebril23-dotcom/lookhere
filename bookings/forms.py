from django import forms
from .models import Booking, Addon
from datetime import time


class TimeSelectWidget(forms.Select):
    """Select widget that renders time choices and handles time object values."""

    TIME_CHOICES = [
        ('', '---------'),
        ('09:00:00', '9:00 AM'),
        ('10:00:00', '10:00 AM'),
        ('11:00:00', '11:00 AM'),
        ('12:00:00', '12:00 PM'),
        ('13:00:00', '1:00 PM'),
        ('14:00:00', '2:00 PM'),
        ('15:00:00', '3:00 PM'),
        ('16:00:00', '4:00 PM'),
        ('17:00:00', '5:00 PM'),
        ('18:00:00', '6:00 PM'),
    ]

    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, choices=self.TIME_CHOICES)

    def format_value(self, value):
        """Convert time object to string so it matches the choice keys."""
        if isinstance(value, time):
            return [value.strftime('%H:%M:%S')]
        if isinstance(value, list):
            return [
                v.strftime('%H:%M:%S') if isinstance(v, time) else v
                for v in value
            ]
        return super().format_value(value)


class BookingAdminForm(forms.ModelForm):
    """Custom form for Booking admin with time dropdown and single addon select."""

    time = forms.TimeField(
        widget=TimeSelectWidget(attrs={'class': 'time-select'}),
        label='Time',
        required=True,
        input_formats=['%H:%M:%S', '%H:%M'],
    )

    # Single addon dropdown — no checkboxes, no multi-select
    addon = forms.ModelChoiceField(
        queryset=Addon.objects.all(),
        widget=forms.Select(attrs={'class': 'addons-select'}),
        required=False,
        label='Add-ons',
        empty_label='---------',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-select the first existing addon when editing
        if self.instance and self.instance.pk:
            existing = self.instance.addons.first()
            if existing:
                self.initial['addon'] = existing.pk

    class Meta:
        model = Booking
        # Exclude the real M2M 'addons' field — we handle it via 'addon' above
        exclude = ['addons']
