from django import forms

from .models import TeeTime

class NewTeeTimeForm(forms.ModelForm):
    class Meta:
        model = TeeTime
        exclude = ("caddy_shack",)

    def __init__(self, *args, **kwargs):
        initial_arguments = kwargs.get('initial', None)
        if initial_arguments:
            caddy = initial_arguments.get("caddy", None)
        elif args:
            caddy = args[0].__getitem__('caddy')

        super().__init__(*args, **kwargs)
        self.fields["caddy"].choices = caddy