from django.urls import path

from . import views

app_name = 'caddymaster'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('teetime/new', views.new_teetime, name='new_teetime'),
    # path('teetime/<int:pk>', views.TeeTimeDetailView.as_view(), name='teetime-detail'),
]