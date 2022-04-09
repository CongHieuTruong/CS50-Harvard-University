from django import forms
from .models import FormModel


class FormData(forms.ModelForm):
    """Form for the image model"""
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
      "placeholder": "Page Title"}))
    text = forms.CharField(label='', widget=forms.Textarea(attrs={
      "placeholder": "Page Content using Github Markdown, click the link above for more infomation."
    }))
    class Meta:
        model = FormModel
        fields = ('title', 'text',  'image')
        

class Search(forms.Form):
    title = forms.CharField(label='', widget=forms.TextInput(attrs={
      "class": "search",
      "placeholder": "Search EWiki"}))