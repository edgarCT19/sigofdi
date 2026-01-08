# utils.py (por ejemplo)
from django.http import Http404

def mongo_get_object_or_404(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise Http404