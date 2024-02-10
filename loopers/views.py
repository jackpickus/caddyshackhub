from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404, Http404
from django.urls import reverse
from django.views import generic, View
from django.views.generic.edit import FormMixin
from django.db.models import F
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.mail import send_mail
from django.db import connection

from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Caddy, Loop
from .forms import NewUserForm, NewLoopForm, FollowCaddyForm, ChangeEmailForm
from loopers import helpers


class IndexView(LoginRequiredMixin, generic.ListView):
    model = Loop
    template_name = "loopers/index.html"
    context_object_name = "all_loops"

    def get_queryset(self):
        # return the last five loops
        return Loop.objects.filter(caddy=self.request.user)[:5]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        total_loops = Caddy.objects.get(user=self.request.user).loop_count
        context["loop_count"] = total_loops

        total_money = Loop.objects.filter(caddy=self.request.user).values_list(
            "money", flat=True
        )
        grand_money_total = 0
        for cash in total_money:
            grand_money_total += cash
        context["total_money"] = grand_money_total

        friends = Caddy.objects.get(user=self.request.user).friends.all()
        friends_loop_dict = {}
        for fri in friends:
            friends_loop_dict.update({fri.loop_count: fri})
        top_three_friends = dict(
            sorted(friends_loop_dict.items(), key=lambda item: item[0], reverse=True)[
                :3
            ]
        )
        context["top_three_friends"] = top_three_friends

        return context


def register(request):
    if request.method == "POST":
        f = NewUserForm(request.POST)
        if f.is_valid():
            activation_key = helpers.generate_activation_key(
                username=request.POST["username"]
            )

            subject = "MyLoopCount Email Verification"
            message = """\n
                Please visit the following link to verify your email \n\n{0}://{1}/loopers/activate/account/?key={2}
                    """.format(
                request.scheme, request.get_host(), activation_key
            )

            error = False

            try:
                send_mail(
                    subject, message, settings.SERVER_EMAIL, [request.POST["email"]]
                )
                messages.add_message(
                    request,
                    messages.INFO,
                    "Account created! Please activate your account by clicking on the link sent to your email.",
                )

            except:
                error = True
                messages.add_message(
                    request,
                    messages.INFO,
                    "Unable to send email verification. Please try again",
                )

            if not error:
                u = User.objects.create_user(
                    request.POST["username"],
                    request.POST["email"],
                    request.POST["password1"],
                    is_active=0,
                )

                caddy = Caddy()
                caddy.activation_key = activation_key
                caddy.user = u
                caddy.save()

            return redirect(reverse("loopers:register"))
    else:
        f = NewUserForm()

    return render(request, "loopers/register.html", {"form": f})


def activate_account(request):
    key = request.GET["key"]
    if not key:
        raise Http404()

    r = get_object_or_404(Caddy, activation_key=key, email_validated=False)
    r.user.is_active = True
    r.user.save()
    r.email_validated = True
    r.save()

    return render(request, "loopers/activated.html")


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Loop
    template_name = "loopers/detail.html"

    # make sure the user can only view their loops and no one else's
    def get_queryset(self):
        return Loop.objects.filter(caddy=self.request.user)


class LoopListView(LoginRequiredMixin, generic.ListView):
    model = Loop
    paginate_by = 10
    template_name = "loopers/loop_list.html"

    def get_queryset(self):
        return Loop.objects.filter(caddy=self.request.user)


@login_required
def new_loop(request):
    if request.method == "POST":
        f = NewLoopForm(request.POST)
        if f.is_valid():
            obj = f.save(commit=False)
            obj.caddy = User.objects.get(pk=request.user.id)

            loops_to_be_added = obj.num_loops
            caddy = Caddy.objects.get(user=request.user.id)
            caddy.loop_count = F("loop_count") + loops_to_be_added
            caddy.save()

            obj.save()
            messages.success(request, "New loop added!")
            return redirect(reverse("loopers:loops"))
    else:
        f = NewLoopForm()

    return render(request, "loopers/new_loop.html", {"form": f})


@login_required
def edit_loop(request, pk):
    try:
        loop_to_edit = Loop.objects.get(pk=pk)
    except:
        raise Http404("Loop does not exist")

    # prevent other users from editing other user's loops
    if loop_to_edit.caddy.id != request.user.id:
        return HttpResponseForbidden("You cannot edit what is not yours")

    if request.method == "POST":
        f = NewLoopForm(request.POST, instance=loop_to_edit)
        if f.is_valid():
            f.save()
            messages.success(request, "Loop has been updated successfully")
            return redirect(reverse("loopers:loops"))
    else:
        f = NewLoopForm(instance=loop_to_edit)

    return render(request, "loopers/edit_loop.html", {"form": f, "item": loop_to_edit})


@login_required
def delete_loop(request, loop_id):
    try:
        loop_to_delete = Loop.objects.get(pk=loop_id)
    except Loop.DoesNotExist:
        raise Http404("Loop does not exist")

    if loop_to_delete.caddy.id != request.user.id:
        return HttpResponseForbidden("Loop does not exist")

    num_loops = loop_to_delete.num_loops

    caddy = Caddy.objects.get(user=request.user.id)
    caddy.loop_count = F("loop_count") - num_loops

    caddy.save()

    loop_to_delete.delete()
    return redirect(reverse("loopers:loops"))


class Settings(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "loopers/settings.html")


@login_required
def change_password(request):
    if request.method == "POST":
        f = PasswordChangeForm(request.user, request.POST)
        if f.is_valid():
            user = f.save()
            update_session_auth_hash(request, user)

            messages.success(request, "Password successfully changed")
            return redirect(reverse("loopers:settings"))
    else:
        f = PasswordChangeForm(request.user)

    return render(request, "loopers/change_password.html", {"form": f})


class FriendsListView(FormMixin, LoginRequiredMixin, generic.ListView):
    context_object_name = "all_friends"
    template_name = "loopers/friends.html"
    form_class = FollowCaddyForm

    def get_queryset(self):
        caddy = Caddy.objects.get(user=self.request.user.id)
        return caddy.friends.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_following = len(Caddy.objects.get(user=self.request.user.id).friends.all())
        context["total_following"] = total_following
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        caddy = Caddy.objects.get(user=request.user.id)

        if form.is_valid():
            caddy_to_follow = request.POST["caddy_to_follow"]
            user = User.objects.get(username=caddy_to_follow)
            if not user.is_staff:
                friend = Caddy.objects.get(user_id=user.id)

                caddy.friends.add(friend.id)
                messages.success(request, "Successfully followed caddy")
                return redirect(reverse("loopers:friends"))

        return render(
            request,
            "loopers/friends.html",
            {"form": form, "all_friends": caddy.friends.all(), "total_following": len(caddy.friends.all())},
        )


def unfollow_friend(request, friend_id):
    caddy = Caddy.objects.get(user=request.user.id)
    caddy.friends.remove(friend_id)
    return redirect(reverse("loopers:friends"))

@login_required()
def followers(request):
    caddy = Caddy.objects.get(user=request.user.id)
    followers = []
    with connection.cursor() as cursor:
        cursor.execute(
            "select from_caddy_id from loopers_caddy_friends where to_caddy_id = %s;",
            [caddy.id],
        )
        for row in cursor.fetchall():
            followers.append(row)

    count = 0
    for x in followers:
        temp = int(x[0])
        followers[count] = temp
        count += 1

    the_followers_username = []
    sum_followers = 0
    for c in followers:
        temp_caddy = Caddy.objects.get(id=c)
        name = temp_caddy.user.username
        the_followers_username.append(name)
        sum_followers += 1

    return render(
        request, "loopers/followers.html", {"followers": the_followers_username, "total": sum_followers}
    )


@login_required()
def change_email(request):
    caddy = Caddy.objects.get(user=request.user.id)

    if request.method == "POST":
        f = ChangeEmailForm(request.POST)
        if f.is_valid():
            password_entered = request.POST["password"]
            new_email = request.POST["new_email"]

            password_match = check_password(password_entered, request.user.password)

            if password_match:
                caddy.change_email = new_email
                caddy.save()

                change_email_key = helpers.generate_activation_key(
                    username=request.user.username
                )

                subject = "Verify your MyLoopCount email address"
                message = """\n
                    Hi there! You recently added the new email address {0} to your account. Please visit the following link to verify your new email \n\n{1}://{2}/loopers/email_verification/?key={3}
                        """.format(
                    new_email, request.scheme, request.get_host(), change_email_key
                )

                error = False

                try:
                    send_mail(
                        subject,
                        message,
                        settings.SERVER_EMAIL,
                        [request.POST["new_email"]],
                    )
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Please verify your new email by clicking on the link sent to the new address.",
                    )

                except:
                    error = True
                    messages.add_message(
                        request,
                        messages.INFO,
                        "Unable to send email verification. Please try again",
                    )
                if not error:
                    caddy.change_email_key = change_email_key

                return redirect(reverse("loopers:settings"))
            else:
                messages.error(request, "password is incorrect")

    else:
        f = ChangeEmailForm(request.POST)

    return render(request, "loopers/change_email.html", {"form": f})


@login_required()
def email_verification(request):
    key = request.GET["key"]
    if not key:
        raise Http404()

    caddy = get_object_or_404(Caddy, change_email_key=key)
    user = request.user
    user.email = caddy.change_email
    user.save()

    messages.success(request, "email successfully changed!")

    return render(request, "loopers/settings.html")