from django.contrib import admin

from .models import Listing, Comment, Bid, Review, Category, Watchlist
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'init_price',
                    'curr_price', 'pub_date', 'end_date']
    list_filter = ['pub_date', 'end_date']
    list_editable = ['init_price']

admin.site.register(Comment)
admin.site.register(Bid)
admin.site.register(Review)
admin.site.register(Watchlist)