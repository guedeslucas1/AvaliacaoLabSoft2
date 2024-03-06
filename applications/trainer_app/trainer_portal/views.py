from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# patient_portal/views.py
# from django.shortcuts import render

# def index(request):
#     return render(request, 'example.html')
