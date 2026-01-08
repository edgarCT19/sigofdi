from django.shortcuts import render

def error_edit (request):
    return render(request, 'Errores/errorEdit_Cap.html') # Renderiza la plantilla de edición de errores