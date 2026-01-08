# systemsigo/decoradores.py
from functools import wraps
from django.shortcuts import redirect

def login_required_custom(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')  # o al nombre de la URL de login
        return view_func(request, *args, **kwargs)
    return _wrapped_view