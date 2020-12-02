# pylint: disable=no-member
from math import ceil
from datetime import timedelta, datetime
#from .managers import ListingManager

from django.urls import reverse
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from autoslug import AutoSlugField


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = AutoSlugField(populate_from='name', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'category': self.slug})

class ActiveListingManager(models.Manager):
    def get_queryset(self):
        return super(ActiveListingManager,
                    self).get_queryset()\
                         .filter(end_date__gt=timezone.now())\
                         .filter(pub_date__lte=timezone.now())
            

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category,
                                 related_name='listings',
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    description = models.TextField(blank=True)
    created_date = models.DateField(auto_now=True)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date ended')
    init_price = models.DecimalField(max_digits=10, decimal_places=2)
    curr_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.URLField()

    slug = AutoSlugField(populate_from='slugify', unique=True, max_length=81)

    objects = models.Manager()
    active = ActiveListingManager()

    def __str__(self):
        return self.name

    def get_bids(self):
        return self.bid_set.all()

    def get_winner(self):
        bids = self.bid_set.all()
        if not bids:
            return None
        return bids[0].bidder


    def is_active(self):
        '''Returns True if active, False otherwise'''
        return self.end_date > timezone.now() >= self.pub_date

    def is_trending(self):
        '''
        Returns True if this listing has 5+ bids
        in the last 24 hours
        '''
        count = self.bid_set.filter(created_date__gte=timezone.now() \
        + timedelta(days=-1)).count()

        return count >= 5

    def save(self, *args, **kwargs):
        # if duration of listing is more than 30 days, prevent from saving
        if (self.pub_date + timedelta(days=30)) < self.end_date:
            return 'Duration cannot be more than 30 days.'
        else:
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('listing', kwargs={'listing_slug': self.slug})

    def slugify(self):
        return f'{self.name} {int(timezone.now().timestamp())}'

    def ends_in(self):
        delta = self.end_date - timezone.now()
        days = delta.days
        seconds = delta.seconds
        hours = seconds // 3600
        minutes = seconds // 60
        if days:
            return f'{days} day' if days == 1 else f'{days} days'
        elif hours > 0:
            return f'{hours} hour' if hours == 1 else f'{hours} hours'
        elif minutes > 0:
            return f'{minutes} minute' if minutes == 1 else f'{minutes} minutes'

        return  f'{seconds} second' if seconds == 1 else f'{seconds} seconds'

    class Meta:
        ordering = ['pub_date']


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    body = models.TextField(max_length=500)
    created_date = models.DateTimeField('date created', auto_now=True)

    def __str__(self):
        return f'{self.author.username}->{self.listing.name}' \
        + f'({self.listing.id})'

    class Meta:
        ordering = ['-created_date']


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created_date = models.DateTimeField('date created', auto_now=True)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.listing.name}->{self.bidder.username}' \
        + f'({str(self.value)})'

    def save(self, *args, **kwargs):
        if not self.listing:
            return
        if self.listing.curr_price:
            if self.listing.curr_price >= self.value:
                # return
                raise ValueError('Price must be higher than current price')            
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-value']

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
    related_name='reviews_to')
    target = models.ForeignKey(User, on_delete=models.CASCADE,
    related_name='reviews_from')
    body = models.TextField(max_length=500)
    rating = models.PositiveSmallIntegerField()
    created_date = models.DateTimeField('date created', auto_now=True)

    def __str__(self):
        return f'{self.author.username}->{self.target.username}' \
        + f'({self.rating})'

    class Meta:
        ordering = ['-created_date']

class ActiveWatchlistManager(models.Manager):
    def get_queryset(self):
        return super(ActiveWatchlistManager,
                    self).get_queryset()\
                         .filter(listing__end_date__gt=timezone.now())\
                         .filter(listing__pub_date__lte=timezone.now())   

class Watchlist(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    listing = models.ManyToManyField(Listing)
    active = ActiveWatchlistManager()
    objects = models.Manager()

    def count(self):
        return self.listing.all().count()

    def __str__(self):
        return f'{self.owner}({self.listing.all().count()})'


from django.dispatch import receiver

@receiver(models.signals.pre_save, sender=Bid)
def validate_bid_value(sender, instance, **kwargs):   
    listing = Listing.objects.get(pk=instance.listing.id)
    if listing.curr_price:
        if listing.curr_price >= instance.value:
            raise ValueError('Bid must be higher than current price')


@receiver(models.signals.post_save, sender=Bid)
def update_listing_price(sender, instance, created, **kwargs):  
    if created:  
        instance.listing.curr_price = instance.value
        instance.listing.save()

@receiver(models.signals.post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        Watchlist.objects.create(owner=instance)