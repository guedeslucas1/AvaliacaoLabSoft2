from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="trainer-portal-index"),
    path("perfil/", views.perfil, name="trainer-portal-perfil"),
    path("agenda/", views.agenda, name="trainer-portal-agenda"),
    path('atletas/', views.atletas, name='trainer-portal-atletas'),
    path('disponibilidade/', views.disponibilidade, name='trainer-portal-disponibilidade'),
    path('disponibilidade/<str:time_slot_id>/<str:add_or_remove>/', views.mudar_disponibilidade, name='trainer-portal-mudar-disponibilidade'),
    path('perfil_atleta/<str:atl_id>', views.perfil_atleta, name='trainer-portal-perfil-atleta'),
    path('timeslots/', views.TimeFrameListCreate.as_view(), name='timeslot-view-create')
]