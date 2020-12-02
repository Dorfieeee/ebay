from django.contrib.auth.models import User
from .models import Category
from django.utils import timezone

def watchlist(request):
    if request.user.is_anonymous:
        return {}

    w = request.user.watchlist.listing\
                                .filter(end_date__gt=timezone.now())\
                                .filter(pub_date__lte=timezone.now())
                                
    return {'watchlist': w, 'categories': Category.objects.all()}
