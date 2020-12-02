from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from auctions.models import Listing, Watchlist
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserRegistrationForm, ProfileForm

@login_required
def dashboard(request):
    return HttpResponseRedirect(reverse('active-listings'))

@login_required
def active_listings(request): 
    active_listings = Listing.active.filter(owner=request.user)
    paginator = Paginator(active_listings, 5)
    page = request.GET.get('page')
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)

    return render(request, 'accounts/dashboard.html', {'listings': listings, 'section': 'active'})

@login_required
def non_active_listings(request):
    non_active_listings = Listing.objects.filter(owner=request.user).filter(end_date__lte=timezone.now())
    paginator = Paginator(non_active_listings, 5)
    page = request.GET.get('page')
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)
    return render(request, 'accounts/dashboard.html', {'listings': listings, 'section': 'non-active'})

@login_required
def watchlist(request):
    return render(request, 'accounts/dashboard.html', {'section': 'watchlist'})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request,
                          'registration/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'registration/register.html',
                  {'user_form': user_form})

@login_required
def my_profile(request):
    if request.method == 'POST':
        instance = request.user.userprofile
        profile_form = ProfileForm(request.POST, instance=instance)
        if profile_form.is_valid():            
            profile_form.save()
    else:    
        profile_form = ProfileForm(initial={'user': request.user})

    return render(request, 'accounts/dashboard.html', {'section': 'my-profile', 'profile_form': profile_form})