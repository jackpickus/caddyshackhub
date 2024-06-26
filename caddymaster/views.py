from django.shortcuts import render
from django.views import generic
from django.contrib.auth.decorators import permission_required

from .models import TeeTime
from .forms import AssignLoopForm

class IndexView(generic.ListView):
    model = TeeTime
    template_name = "caddymaster/index.html"

@permission_required("caddymaster.can_create_teetimes")
def new_teetime(request):
    if request.method == "POST":
        f = AssignLoopForm(request.POST)
        if f.is_valid():
            print("Save Loop and Assign to caddy")
    else:
        f = AssignLoopForm()

    return render(request, "caddymaster/assign_loop.html", {"form": f})

