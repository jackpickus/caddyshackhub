from django.shortcuts import render
from django.views import generic

from .models import CaddyMaster, CaddyShack

class IndexView(generic.ListView):
    model = CaddyMaster
    template_name = 'caddymaster/index.html'

