from django.urls import path

from . import views

app_name = 'caddymaster'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('teetime/new', views.new_teetime, name='new_teetime'),
    path('teetime/<int:pk>', views.TeeTimeDetailView.as_view(), name='teetime-detail'),
    path('teetime/<int:pk>/edit_teetime', views.edit_teetime, name='edit_teetime'),
    path("teetime/delete/<int:teetime_id>", views.delete_teetime, name="delete_teetime"),
]