from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="trainer-portal-index"),
    path("pacientes/", views.patients, name="trainer-portal-patient"),
]