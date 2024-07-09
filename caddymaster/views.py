from django.http import Http404, HttpResponseForbidden
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import generic
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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

def edit_teetime(request, pk):
    try:
        teetime_to_edit = TeeTime.objects.get(pk=pk)
    except:
        raise Http404("Teetime does not exist")

    if teetime_to_edit.caddy_shack.caddy_master.user.id != request.user.id:
        return HttpResponseForbidden()

    if request.method == "POST":
        f = NewTeeTimeForm(request.POST, instance=teetime_to_edit)
        if f.is_valid():
            f.save()
            messages.success(request, "TeeTime has been updated")
            return redirect(reverse("caddymaster:index"))
    else:
        caddies_in_shack = teetime_to_edit.caddy_shack.caddys.all()
        caddy_names = []
        for caddy in caddies_in_shack:
            # Skip caddy already assigned to teetime
            if caddy.id == teetime_to_edit.caddy.id:
                continue

            the_caddy_obj = []
            the_caddy_obj.append(caddy.id)
            the_caddy_obj.append(caddy.username) 
            caddy_names.append(tuple(the_caddy_obj)) # the 'caddy' object is really a User object

        # Add caddy already assigned w/teetime to front of list
        init_caddy = []
        init_caddy.append(str(teetime_to_edit.caddy.id))
        init_caddy.append(teetime_to_edit.caddy.username)
        caddy_names.insert(0, tuple(init_caddy))

        f = NewTeeTimeForm(instance=teetime_to_edit, initial={"caddy": caddy_names})

    return render(request, "caddymaster/edit_teetime.html", {"form": f, "item": teetime_to_edit})

@login_required
def delete_teetime(request, teetime_id):
    try:
        teetime = TeeTime.objects.get(pk=teetime_id)
    except TeeTime.DoesNotExist:
        raise Http404("TeeTime does not exist")

    if teetime.caddy_shack.caddy_master.user.id != request.user.id:
        return HttpResponseForbidden()

    teetime.delete()
    return redirect(reverse("caddymaster:index"))