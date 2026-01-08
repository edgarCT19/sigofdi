from decimal import Decimal, ROUND_HALF_UP

from datetime import datetime 

from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages

def is_admin(user):
    # Ajusta si tu rol exacto es 'admin', 'administrador' o similar
    return bool(user and getattr(user, "rol", "").lower() in ["admin", "administrador"])

def get_periodo_activo(PeriodoInventario):
    return PeriodoInventario.objects(status="Activo").first()

def parse_decimal(value, q='0.01'):
    return Decimal(value).quantize(Decimal(q), rounding=ROUND_HALF_UP)
