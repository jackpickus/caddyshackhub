from django import forms

from .models import TeeTime

class NewTeeTimeForm(forms.ModelForm):
    class Meta:
        model = TeeTime
        exclude = ["caddy_shack"]