from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('n1ed/', include('n1ed.urls')),
    path('editor/<str:kind>/', views.editor),
]
