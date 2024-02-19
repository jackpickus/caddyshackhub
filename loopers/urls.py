from django.urls import path

from . import views

app_name = "loopers"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("register/", views.register, name="register"),
    path("activate/account/", views.activate_account, name="activate"),
    path("loops/", views.LoopListView.as_view(), name="loops"),
    path("loop/<int:pk>", views.DetailView.as_view(), name="loop-detail"),
    path("loop/new_loop/", views.new_loop, name="new_loop"),
    path("loop/<int:pk>/edit_loop", views.edit_loop, name="edit_loop"),
    path("loop/delete/<int:loop_id>", views.delete_loop, name="delete_loop"),
    path("settings/", views.Settings.as_view(), name="settings"),
    path("settings/change_password/", views.change_password, name="change_password"),
    path("settings/change_email/", views.change_email, name="change_email"),
    path("settings/delete-account/<int:pk>", views.DeleteAccount.as_view(), name="delete_account"),
    path("email_verification/", views.email_verification, name="email_verification"),
    path("friends/", views.FriendsListView.as_view(), name="friends"),
    path(
        "friends/delete/<int:friend_id>", views.unfollow_friend, name="unfollow_friend"
    ),
    path("friends/followers/", views.followers, name="followers"),
    path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
]
