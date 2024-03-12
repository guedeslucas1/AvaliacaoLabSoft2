from django.shortcuts import render

users = [
    {
        'name': 'Lucas',
        'email': 'guedeslucas@usp.br',
        'peso': '75 Kg'
    },
    {
        'name': 'joão',
        'email': 'joãojoão@usp.br',
        'peso': '57 Kg'
    },
]


def index(request):
    return render(request, 'trainer_portal/home.html')

def patients(request):
    context = {
        'users': users
    }
    return render(request, 'trainer_portal/patients.html', context)


