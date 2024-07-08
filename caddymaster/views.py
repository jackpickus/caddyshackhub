from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import permission_required
from django.contrib import messages

from .models import TeeTime, CaddyMaster, CaddyShack
from .forms import NewTeeTimeForm

class IndexView(generic.ListView):
    model = TeeTime
    template_name = "caddymaster/index.html"

@permission_required("caddymaster.can_create_teetimes", raise_exception=True)
def new_teetime(request):
    cm = CaddyMaster.objects.get(user=request.user.id)
    caddyshack = CaddyShack.objects.get(caddy_master=cm)
    if request.method == "POST":
        f = NewTeeTimeForm(request.POST)
        if f.is_valid():
            teetime = f.save(commit=False)
            teetime.caddy_shack = caddyshack
            teetime.save()
            messages.success(request, "TeeTime created!")
            return render(request, "caddymaster/index.html")
    else:
        # get caddies and prefill dropdown list in form
        caddies_in_shack = caddyshack.caddys.all() # this is a list of User objects
        caddy_names = []
        for caddy in caddies_in_shack:
            the_caddy_obj = []
            the_caddy_obj.append(caddy.id)
            the_caddy_obj.append(caddy.username) 
            caddy_names.append(tuple(the_caddy_obj)) # the 'caddy' object is really a User object
            

        f = NewTeeTimeForm(initial={"caddy": caddy_names})

    return render(request, "caddymaster/new_teetime.html", {"form": f})

class TeeTimeDetailView(generic.DetailView):
    model = TeeTime
    template_name = "caddymaster/teetime_details.html"