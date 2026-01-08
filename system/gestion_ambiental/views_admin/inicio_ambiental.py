from django.shortcuts import render

def inicio_ambiental(request):
    return render(request, 'systemsigo_ambiental/Ambiental/index.html')