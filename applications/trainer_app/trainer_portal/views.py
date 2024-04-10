from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import calendar
from calendar import HTMLCalendar
from datetime import datetime, timedelta  
from django.http import HttpResponseRedirect
from django.urls import reverse
import pytz
from .models import TimeSlot
from django.shortcuts import render
from rest_framework import generics
from .serializers import TimeSlotSerializer

class TimeFrameListCreate(generics.ListAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


events = [
    {
        "day": 1,
        "month": 5,
        "time": "8:30",
        "description": "Treinamento de Jorge",
        "recurrency": 0,
    },
    {
        "day": 8,
        "month": 4,
        "time": "8:30",
        "description": "Treinamento de João",
        "recurrency": 7,
    },
    {
        "day": 11,
        "month": 4,
        "time": "8:30",
        "description": "Treinamento de Maria",
        "recurrency": 14
    },
]


athletes = [
    {
        "id": 120,
        "name": "Jorge Silva",
        "email": "jorgesilva@gmail.com",
        "age": 35,
        "weight": 80,
        "height": 80,
        "gender": "Masculino",
        "obs_doctor": "Jorge tem problemas nos ossos.",
        "obs_nutri": "Jorge está fazendo um regime radical.",
        "obs_psic": "Jorge está fazendo tratamento para ansiedade.",
        
    },
    {
        "id": 122,
        "name": "João",
        "age": 70,
        "weight": 75,
        "height": 80,
        "gender": "Masculino",
    },
    {
        "id": 123,
        "name": "Maria",
        "email": "emaildamaria@bing.com",
        "age": 30,
        "weight": 62,
        "height": 80,
        "gender": "Feminino",
        "obs_doctor": "Maria tem asma.",
        "obs_nutri": "Maria está fazendo uma dieta baseada em carboidratos.",
        "obs_psic": "Maria teve alta das consultas.",

    },
]

def index(request):
    return render(request, 'users/register.html')


def is_event_on_day(event, target_day, target_month):
    if (target_day == 0):
        return False
    # If recurrency is 0, the event occurs only on the specified day
    if event['recurrency'] == 0:
        return event['day'] == target_day and event['month'] == target_month

    # Calculate the target date and the event date
    target_date = datetime.date(datetime.date.today().year, target_month, target_day)
    event_date = datetime.date(datetime.date.today().year, event['month'], event['day'])

    # Calculate the difference in days between the event and target dates
    days_difference = (target_date - event_date).days

    # Check if the event falls on the target day or any subsequent occurrence
    if days_difference >= 0 and days_difference % event['recurrency'] == 0:
        return True
    else:
        return False

@login_required
def agenda(request):
    return render(request, 'trainer_portal/agenda.html',
        {}
    )

def check_available(request, start_time):
    start_time = start_time.astimezone(pytz.utc) - timedelta(hours=3)
    user_test = User.objects.get(username=request.user) 
    for slots in TimeSlot.objects.filter(professional_id=user_test):
        if slots.time == start_time:
            return True
    return False

@login_required
def mudar_disponibilidade(request, time_slot_id, add_or_remove):
    start_time = datetime.strptime(time_slot_id.split(' GMT')[0], '%a %b %d %Y %H:%M:%S')
    start_time = start_time.astimezone(pytz.utc) - timedelta(hours=3)

    add_time_slot = (add_or_remove == '1')

    exists = False

    for slots in TimeSlot.objects.filter(professional_id=request.user):
        if slots.time == start_time:
            if add_time_slot:
                return redirect(reverse('trainer-portal-disponibilidade'))
            else:
                slots.delete()
            
    if add_time_slot:
        new_time_slot = TimeSlot(time = start_time, professional_id = request.user)
        new_time_slot.save()
    return redirect(reverse('trainer-portal-disponibilidade'))

@login_required
def disponibilidade(request):
    events = list()

    # Define o intervalo de 4 meses
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)  # 4 meses = 120 dias

    # Loop através de todas as datas no intervalo
    current_date = start_date
    while current_date < end_date:
        # Define o horário de início e fim para cada dia
        start_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=6)
        end_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=20)

        # Loop através de todas as horas no intervalo
        while start_time < end_time:
            # Cria um evento para cada hora
            is_available = check_available(request, start_time) 
            background = '#90EE90'
            if not is_available:
                background = '#FF7F7F'
            
            event = {
                'title': 'Evento',
                'start': start_time.strftime('%Y-%m-%dT%H:%M:%S'),  # Formato ISO 8601
                'end': (start_time + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),  # 1 hora de duração
                'backgroundColor': background
            }
            events.append(event)

            # Incrementa o horário de início para a próxima hora
            start_time += timedelta(hours=1)

        # Incrementa a data para o próximo dia
        current_date += timedelta(days=1)

    return render(request, 'trainer_portal/disponibilidade.html', {'events': events})

def cadastro(request):
    return render(request, 'trainer_portal/cadastro.html')

def perfil(request):
    return render(request, 'trainer_portal/perfil.html',
    {
        'context': {
            'name':  request.user.username,
            'email': request.user.email,
        }
    })


@login_required
def atletas(request):

    athletes_view = list()

    counter = 0
    
    athletes_row = list()
    for a in athletes:
        athletes_row.append(a)
        counter += 1 

        if counter >= 4:
            counter = 0
            athletes_view.append(athletes_row)
            athletes_row = list()

    athletes_view.append(athletes_row)


    return render(request, 'trainer_portal/atletas.html',
        {
            "athletes_view":athletes_view
        }
    )

def perfil_atleta(request, atl_id):

    atl_data = dict()
    for atl in athletes:
        if atl["id"] == int(atl_id):
            atl_data = atl

    return render(request, 'trainer_portal/perfil_atleta.html', {"atl_data": atl_data})