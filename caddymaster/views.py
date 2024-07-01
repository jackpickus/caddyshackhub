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
    if request.method == "POST":
        f = NewTeeTimeForm(request.POST)
        if f.is_valid():
            teetime = f.save(commit=False)
            cm = CaddyMaster.objects.get(user=request.user.id)
            caddyshack = CaddyShack.objects.get(caddy_master=cm)
            teetime.caddy_shack = caddyshack
            teetime.save()
            messages.success(request, "TeeTime created!")
            return render(request, "caddymaster/index.html")
    else:
        cm = CaddyMaster.objects.get(user=request.user.id)
        print(cm.user.get_all_permissions())
        print("Caddymaster permissions")
        f = NewTeeTimeForm()

    return render(request, "caddymaster/new_teetime.html", {"form": f})
