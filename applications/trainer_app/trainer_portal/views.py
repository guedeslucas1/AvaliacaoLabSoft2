from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse

import calendar
from calendar import HTMLCalendar
from datetime import datetime, timedelta  
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.conf import settings
import pytz
import json
import requests

from django.contrib.auth.models import User
from .models import TimeSlot
from .serializers import (TimeSlotSerializer, UserSerializer)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import generics, viewsets

from drf_yasg.utils import swagger_auto_schema

import boto3

def download_pdf(request, atl_id, user_id, file_name):

    key = atl_id+"/personal trainer/"+user_id+"/"+file_name
    try:
        object_data = search_from_s3(key)

        # Retorna o conteúdo do arquivo PDF como uma resposta HTTP
        response = HttpResponse(object_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="arquivo_{file_name}.pdf"'
        return response

    except Exception as e:
        # Retorna uma resposta indicando que o arquivo não foi encontrado
        return HttpResponse(f'Ocorreu um erro ao baixar o arquivo: {e}', status=500)

#S3
def upload_to_s3(file_obj, file_key):
    s3 = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    s3.upload_fileobj(file_obj, bucket_name, file_key)

def search_from_s3(file_key):
     # Conecta-se ao S3
    s3 = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    # Lista todos os objetos no bucket
    response = s3.list_objects_v2(Bucket=bucket_name)

    # Verifica se o arquivo está presente no bucket    
    for obj in response.get('Contents', []):

        if obj['Key'] == file_key:
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
            object_data = response['Body'].read()
            return object_data

#PATIENT API ENDPOINTS
base_endpoint = "http://ec2-52-67-134-153.sa-east-1.compute.amazonaws.com:8000/api/"

#API CALLS TO FEED OTHER APPLICATIONS
class TimeSlotsViewSet(ViewSet):
    @swagger_auto_schema(
        method='get',
        responses={200: TimeSlotSerializer(many=True)},
        operation_description="Retrieve a list of time slots."
    )
    @action(detail=False, url_path='')
    def all(self, request):
        time_slots = TimeSlot.objects.all()
        serializer = TimeSlotSerializer(time_slots, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        responses={200: TimeSlotSerializer(many=True)},
        operation_description="Retrieve a list of time slots for a given professional."
    )
    @action(detail=False, url_path='(?P<trainer_id>\d+)')
    def professional_patients(self, request, trainer_id):
        time_slots = TimeSlot.objects.filter(professional_id=trainer_id)
        serializer = TimeSlotSerializer(time_slots, many=True)
        a = list()
        for slot in serializer.data:
            a.append(slot["time"][:-1])
        return Response(a)

class UserViewSet(ViewSet):
    @swagger_auto_schema(
        method='get',
        responses={200: UserSerializer()},
        operation_description="Retrieve a list of users."
    )
    @action(detail=False, methods=['get'])
    def all(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        responses={200: UserSerializer()},
        operation_description="Retrieve information of a single user."
    )
    @action(detail=False, methods=['get'], url_path='(?P<user_id>\d+)')
    def trainer_details(self, request, user_id):
        users = User.objects.get(pk=user_id)
        serializer = UserSerializer(users)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        responses={200: UserSerializer()},
        operation_description="Retrieve information availability of all trainers."
    )
    @action(detail=False, methods=['get'], url_path='time_slots')
    def trainer_time_slots(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many = True)

        for u in serializer.data:
            week_days = set()
            for slot in TimeSlot.objects.filter(professional_id=u["id"]):
                week_days.add(slot.time.weekday())

            u["days_available"] = list(week_days)
        
        return Response(serializer.data)



athletes = list()

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
    
    response = requests.get(base_endpoint+"appointments/")

    appointments = response.json()

    events = list()
    for ap in appointments:
        if ap['profession'] == 'Personal Trainer' and ap['professional_id'] == request.user.id:
            patient_id = ap['patient_id']

            patient_data = requests.get(base_endpoint+"patients/"+str(patient_id)+"/details/").json()

            events.append(
                {
                    'title': patient_data["name"],
                    'start': ap['time'][:-1],  # Formato ISO 8601
                    'end': (datetime.strptime(ap['time'][:-1], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),  # 1 hora de duração
                }
            )

    
    return render(request, 'trainer_portal/agenda.html',
        {'events': events}
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
    end_date = start_date + timedelta(days=120)  # 4 meses = 120 dias

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
    global athletes
    response = requests.get(base_endpoint+"appointments/")

    appointments = response.json()
    athletes = list()
    for ap in appointments:
        print(ap['profession'], 'Personal Trainer', ap['professional_id'], request.user.id)
        if ap['profession'] == 'Personal Trainer' and ap['professional_id'] == request.user.id:
            patient_id = ap['patient_id']

            patient_data = requests.get(base_endpoint+"patients/"+str(patient_id)+"/details/").json()
            print("dados do paciente:", patient_data)
            athletes.append(patient_data)

    # athletes = list()
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
    documents = requests.get(base_endpoint+"patients/"+str(atl_id)+"/personal trainer/"+str(request.user.id)+"/getdocuments/").json()
 
    if request.method == 'POST':
        # Verifica se o campo de arquivo foi enviado e não está vazio
        if 'file' in request.FILES and request.FILES['file']:
            file_obj = request.FILES['file']
            key = str(atl_id)+"/personal trainer/"+str(request.user.id)+"/"+file_obj.name
            
            # post to patient API
            data = {'key': key}
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            url = base_endpoint +"patients/"+ str(atl_id)+"/personal trainer/"+str(request.user.id)+"/postdocuments/"
            response = requests.post(url, data=json_data, headers=headers)
            print("Response de envio de arquivo:", response)
            upload_to_s3(file_obj, key) #TODO automatizar upload de arquivo
        elif 'observation' in request.POST:
            content = request.POST.get('observation')
            data = {'observation': content}
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            url = base_endpoint +"patients/"+ str(atl_id)+"/personal trainer/"+str(request.user.id)+"/observation/"
            response = requests.post(url, data=json_data, headers=headers)

    atl_data = requests.get(base_endpoint+"patients/"+str(atl_id)+"/details/").json()
    atl_data["files"] = list()
    for doc in documents:         
        print(doc["key"].split("/"), doc["key"].split("/")[-1])
        atl_data["files"].append(
            {
                "id": str(doc["key"]),
                "file_name":str(doc["key"].split("/")[-1]),
                "atl_id": str(atl_data["id"]),
                "user_id": str(request.user.id),
            }
        )

    atl_data["height"] /= 100
    if atl_data["gender"]=="female":
        atl_data["gender"]="Feminino"
    elif atl_data["gender"]=="male":
        atl_data["gender"] = "Masculino"


    return render(request, 'trainer_portal/perfil_atleta.html', {"atl_data": atl_data})

def chat_atleta(request, atl_id):

    atl_data = dict()
    for atl in athletes:
        if atl["id"] == int(atl_id):
            atl_data = atl
    return render(request, 'trainer_portal/chat.html', {"atl_data": atl_data})