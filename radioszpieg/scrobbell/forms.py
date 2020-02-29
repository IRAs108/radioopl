from django import forms
from .models import Song


class SimpleEditSong(forms.Form):
    clip = forms.CharField(label="Klip youtube", max_length=150)
    spo_uri = forms.CharField(label="Spotify URI", max_length=50)
    rok = forms.IntegerField(label="Rok wydania")
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    us_sp = forms.BooleanField(label="Usuń spotify", required=False)

