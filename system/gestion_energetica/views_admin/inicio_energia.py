from django.shortcuts import render

def inicio_energia(request):
    return render(request, 'systemsigo/Energia/index.html')