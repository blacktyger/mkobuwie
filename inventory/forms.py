
from django import forms
from .models import Stock


class StockForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):  # used to set css classes to the various fields
        super().__init__(*args, **kwargs)
        self.fields['nazwa'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['kategoria'].widget.attrs.update({'class': 'select form-control'})
        self.fields['informacje'].widget.attrs.update({'class': 'textinput form-control', 'placeholder': 'Dodatkowe informacje'})
        self.fields['ilosc'].widget.attrs.update({'class': 'numberinput form-control', 'min': '0'})
        self.fields['cena'].widget.attrs.update({'class': 'numberinput form-control', 'min': '0'})

    class Meta:
        model = Stock
        exclude = ['id', 'is_deleted', 'name', 'wartosc', 'barcode', 'quantity', 'price', 'numer_produktu']
