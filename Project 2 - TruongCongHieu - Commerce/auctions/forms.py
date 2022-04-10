from django import forms
from .models import Category, Auction, Person


class AuctionForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Auction
        fields = ('title', 'description', 'starting_bid', 'category', 'person', 'image')
        widgets = {'category' : forms.Select(choices=Category.objects.all(), attrs={'class' : 'form-control'}),
                   'description': forms.TextInput(attrs={'class': 'form-control'}),
                   'title': forms.TextInput(attrs={'class': 'form-control'}),
                   'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
                   'person' : forms.Select(choices=Person.objects.all(), attrs={'class' : 'form-control'})
                   } 