# -*- coding: utf-8 -*-

from django import forms

from models import Picture, PictureDescription

class PictureDescriptionForm(forms.ModelForm):
    class Meta:
        model = PictureDescription
        exclude = ('picture','i18n')
        
class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        exclude = ('image','thumb','title','rating','number_of_ratings')
        