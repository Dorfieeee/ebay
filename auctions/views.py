# pylint: disable=no-member
from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import json
from .models import Category, User, Listing, Bid, Comment, Review, Watchlist
from .forms import CreateListingForm, CommentEntryForm

# Show the most recent and the soonest ending listings, 10 each
def index(request):
    listings = Listing.active.all()

    # get 10 newest listings
    newest_list = Listing.active.order_by('-pub_date')[:10]

    # get 10 ending soon listings
    ending_list = Listing.active.order_by('end_date')[:10]

    # get 10 trending listings, bid_count_in_last_24hr > 20
    # 10 random ones from trending list...
    from random import sample
    trending_list = [l for l in listings if l.is_trending()]
    trending_list = sample(trending_list, len(trending_list))

    context = {
        'newest': newest_list,
        'ending': ending_list,
        'trending': trending_list,
        'categories': Category.objects.all(),
        'title': 'Homepage',
    }

    return render(request, 'auctions/index.html', context)

# Show individual listing page and accept comment form
def listing(request, listing_slug):
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = CommentEntryForm(request.POST)
            if form.is_valid():
                form.save()
        
        listing_pk = request.POST.get('listing')
        listing = Listing.objects.get(pk=listing_pk)
        return HttpResponseRedirect(reverse('listing',
                                    kwargs={'listing_slug': listing.slug}))
        
    else:    
        listing = get_object_or_404(Listing, slug=listing_slug)

        context = {
            'listing': listing,
            'bids': listing.bid_set.all(),
            'price': listing.curr_price or listing.init_price,
        }

        if request.user.is_authenticated:
            initial = {'listing': listing, 'author': request.user}
            context['comment_entry_form'] = CommentEntryForm(initial=initial)

        return render(request, 'auctions/listing.html', context)

# Show form for placing listings and accepting them
@login_required
def create_listing(request):
    # POST
    if request.method == 'POST':
        form = CreateListingForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            listing = Listing(owner=request.user,
                              name=cd['name'],
                              description=cd['description'],
                              pub_date=cd['pub_date'],
                              end_date=cd['end_date'],
                              init_price=cd['init_price'],
                              image=cd['image'],
                              category=Category.objects.get(name=cd['category']))
            listing.save()

            return HttpResponseRedirect(reverse('listing',
                                        kwargs={'listing_slug': listing.slug}))
        else:
            return render(request, 'auctions/create.html', {'form': form})

        return HttpResponseRedirect('/')
    # GET
    else:
        form = CreateListingForm()
        return render(request, 'auctions/create.html', {'form': form})

# API for add/remove listing from watchlist
@login_required
def watchlist(request):
    # POST
    if request.method == 'POST':
        data = json.loads(request.body)
        listing = Listing.objects.get(slug=data['listing_slug'])
        watchlist = request.user.watchlist.listing
        if listing in watchlist.all():
            watchlist.remove(listing)
            action = 'removed'
        else:
            watchlist.add(listing)
            action = 'added'


        return JsonResponse({
            'watchlist_count': request.user.watchlist.listing\
                                    .filter(end_date__gt=timezone.now())\
                                    .filter(pub_date__lte=timezone.now())\
                                    .count(),
                             'action': action})
    # GET
    else:
        return HttpResponseRedirect(reverse('listing',\
                    kwargs={'listing_slug': request.GET['listing_slug']}))

# API for accepting bids
@login_required
def bid(request):
    # POST
    if request.method == 'POST':
        data = json.loads(request.body)      

        from .forms import BidEntryForm
        form = BidEntryForm(data)
        if form.is_valid():
            cd = form.cleaned_data      

            try:
                listing = Listing.objects.get(slug=cd['listing_slug'])
            except Listing.DoesNotExist as error:
                return JsonResponse({'success': 'false',
                                     'error': error.__str__()})

            if listing.owner == request.user:
                return JsonResponse({'success': 'false',
                                    'error': 'Owner cannot bid on his own listing.'})

            if not listing.is_active():
                return JsonResponse({'success': 'false',
                                     'error': 'Sorry, this auction has already ended.'})

            curr_price = listing.curr_price or listing.init_price    

            if curr_price >= cd['bid_value']:
                return JsonResponse({'success': 'false',
                                     'error': 'The bid must be higher than the current price'})                     
            
            bid = Bid(listing=listing, bidder=request.user, value=cd['bid_value'])
            bid.save()

            return JsonResponse({'success': 'true',
                                'curr_price': listing.curr_price,
                                'msg': 'Your bid was placed successfully.'})
        
        return JsonResponse({'success': 'false',
                                    'error': 'Form validation failed'})

    # GET
    else:
        return HttpResponseRedirect(reverse('listing',\
                    kwargs={'listing_slug': request.GET.get('listing_slug')}))

# API for immediate closure of listing
@login_required
def close_listing(request):
    from django.contrib import messages
    origin = request.META['HTTP_REFERER']
    if request.method == 'POST':
        listing_slug = request.POST.get('listing_slug')
        if not listing_slug:
            messages.error(request, 'Missing identifier for this listing.', extra_tags='alert alert-danger')
            return HttpResponseRedirect(origin)
        try:
            listing = Listing.active.get(slug=listing_slug)
        except Listing.DoesNotExist:
            messages.error(request, 'Listing is not active anymore.', extra_tags='alert alert-danger')
            return HttpResponseRedirect(reverse('listing', kwargs={'listing_slug': listing_slug}))
        if listing.owner != request.user:
            messages.error(request, 'Only owner of this listing can close it.', extra_tags='alert alert-danger')
            return HttpResponseRedirect(reverse('listing', kwargs={'listing_slug': listing_slug}))

        listing.end_date = timezone.now()
        listing.save()
        
        messages.success(request, 'Listing %s was closed successfully' % listing.name, extra_tags='alert alert-success')
        return HttpResponseRedirect(reverse('listing', kwargs={'listing_slug': listing_slug}))
    else:    
        return HttpResponseRedirect(origin)

# Show all active listings for particular category
def category(request, category_slug):
    listing_list = Listing.active.filter(category__slug__iexact=category_slug)
    paginator = Paginator(listing_list, 5)
    page = request.GET.get('page')
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)

    return render(request,
                    'auctions/category_list.html',
                        {'listings': listings,
                        'category': Category.objects.get(slug=category_slug),
                        'page': page})


# Create profile page where anyone can see user's listings (active, not active)
# If logged_in, also show watchlist and active listings he has placed bid on
def profile(request, username):
    user = get_object_or_404(User, username__iexact=username)
    active_listings = Listing.active.filter(owner=user)
    paginator = Paginator(active_listings, 5)
    page = request.GET.get('page')
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)


    return render(request, 'auctions/profile.html', {'usr': user, 'listings': listings, 'page': page})
