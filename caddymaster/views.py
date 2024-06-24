from django.shortcuts import render
from django.views import generic

from .models import TeeTime

class IndexView(generic.ListView):
    model = TeeTime
    template_name = "caddymaster/index.html"
    # context_object_name = "all_tee_times"

