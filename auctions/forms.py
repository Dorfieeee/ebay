# pylint: disable=no-member
from django import forms
from .models import Category, Comment, Listing
from django.utils import timezone
from django.db import models

class CreateListingForm(forms.Form):

        name = forms.CharField(max_length=70, label='Product name')
        category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
        image = forms.URLField(label='Main image', initial='https://')
        pub_date = forms.SplitDateTimeField(initial=timezone.now(),
                                        help_text='Insert date and time when' \
                                                + ' should be listing published.',
                                        label='Publish date')
        end_date = forms.SplitDateTimeField(help_text='Insert date and time when' \
                                                + ' should listing end.',
                                        label='End date')
        init_price = forms.DecimalField(label='Starting price', initial=0)
        description = forms.CharField(widget=forms.Textarea())


# Ready to implement form from class
#
# class CreateListingForm(forms.ModelForm):
#         class Meta:
#                 model = Listing
#                 fields = ['name', 'category', 'image', 'pub_date', 'end_date', 'init_price', 'description']
#                 widgets = {
#                         'category': forms.ModelChoiceField(queryset=Category.objects.all(), required=True),
#                         'description': forms.CharField(widget=forms.Textarea()),
#                         'end_date': forms.SplitDateTimeField(),
#                         'pub_date': forms.SplitDateTimeField(initial=timezone.now()),
#                 }
#                 labels = {
#                         'name': 'Product name',
#                         'image': 'Main image',
#                         'pub_date': 'Publish date',
#                         'end_date': 'End date',
#                         'init_price': 'Starting price',
#                 }



class BidEntryForm(forms.Form):
        bid_value = forms.DecimalField(max_digits=10, decimal_places=2)
        listing_slug = forms.SlugField()

class CommentEntryForm(forms.ModelForm):
        class Meta:
                model = Comment
                fields = ['body', 'listing', 'author']
                widgets = {
                        'listing': forms.HiddenInput(),
                        'author': forms.HiddenInput(),
                        'body': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
                }
                labels = {
                        'body': 'Add comment'
                }


