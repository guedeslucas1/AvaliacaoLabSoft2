from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import TimeSlotsViewSet, UserViewSet

router = DefaultRouter()
router.register(r'time_slots', TimeSlotsViewSet, basename='TimeSlotsViewSet')
router.register(r'users', UserViewSet, basename='UserViewSet')
# router.register(r'documents', DocumentViewSet)
# router.register(r'professionals', CustomProfessionalViewSet, basename='professionals')
# router.register(r'patients', CustomPatientViewSet, basename='patients')

urlpatterns = [
    path("", views.index, name="trainer-portal-index"),
    path("perfil/", views.perfil, name="trainer-portal-perfil"),
    path("agenda/", views.agenda, name="trainer-portal-agenda"),
    path('atletas/', views.atletas, name='trainer-portal-atletas'),
    path('disponibilidade/', views.disponibilidade, name='trainer-portal-disponibilidade'),
    path('disponibilidade/<str:time_slot_id>/<str:add_or_remove>/', views.mudar_disponibilidade, name='trainer-portal-mudar-disponibilidade'),
    path('perfil_atleta/<str:atl_id>', views.perfil_atleta, name='trainer-portal-perfil-atleta'),
    path('perfil_atleta/<str:atl_id>/chat', views.chat_atleta, name='trainer-portal-chat-atleta'),
    # path('timeslots/', views.TimeFrameListCreate.as_view(), name='timeslot-view-create')
    path('api/', include(router.urls)),
    path('download_pdf/<str:atl_id>/<str:user_id>/<str:file_name>/', views.download_pdf, name='download_pdf'),
]
