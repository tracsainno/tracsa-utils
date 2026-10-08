from django.urls import path

from . import views

app_name = 'n1ed'

urlpatterns = [
    path('upload/', views.upload, name='upload'),
]
