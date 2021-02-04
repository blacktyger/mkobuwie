from django import forms
from django.forms import formset_factory
from .models import (
    Supplier,
    PurchaseBill,
    PurchaseItem,
    PurchaseBillDetails,
    SaleBill,
    SaleItem,
    SaleBillDetails, Transakcja
    )
from inventory.models import Stock


class TransakcjaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cena'].widget.attrs.update({'class': 'numberinput form-control col-5', 'id': 'cena', 'required': 'false'})
        self.fields['ilosc'].widget.attrs.update({'class': 'numberinput form-control col-5', 'id': 'ilosc', 'required': 'false'})
        self.fields['rabat'].widget.attrs.update({'class': 'numberinput form-control col-5', 'id': 'rabat', 'required': 'false'})
        self.fields['wartosc'].widget.attrs.update({'class': 'numberinput form-control col-5', 'id': 'wartosc', 'disabled': 'true'})
        self.fields['vat_procent'].widget.attrs.update({'class': 'selectinput form-control', 'id': 'vat_procent', 'required': 'false'})
        self.fields['vat_wartosc'].widget.attrs.update({'class': 'numberinput form-control col-5', 'id': 'vat_wartosc', 'required': 'false'})
        self.fields['produkt'].widget.attrs.update({'class': 'textinput form-control col-5', 'id': 'produkt'})
        self.fields['uwagi'].widget.attrs.update({'class': 'textinput form-control', 'id': 'uwagi', 'required': 'false'})
        # self.fields['czas'].widget.attrs.update({'class': 'dateinput form-control', 'id': 'czas', 'required': 'false'})

    class Meta:
        model = Transakcja
        fields = ['cena', 'ilosc', 'rabat', 'uwagi', 'vat_procent', 'produkt', 'wartosc', 'vat_wartosc']


TransakcjaFormset = formset_factory(TransakcjaForm, extra=1)


# form used to select a supplier
class SelectSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_deleted=False)
        self.fields['supplier'].widget.attrs.update({'class': 'textinput form-control'})

    class Meta:
        model = PurchaseBill
        fields = ['supplier']


# form used to render a single stock item form
class PurchaseItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.filter(is_deleted=False)
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update(
            {'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        self.fields['perprice'].widget.attrs.update(
            {'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})

    class Meta:
        model = PurchaseItem
        fields = ['stock', 'quantity', 'perprice']


# formset used to render multiple 'PurchaseItemForm'
PurchaseItemFormset = formset_factory(PurchaseItemForm, extra=1)


# form used to accept the other details for purchase bill
class PurchaseDetailsForm(forms.ModelForm):
    class Meta:
        model = PurchaseBillDetails
        fields = ['eway', 'veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']


# form used for supplier
class SupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'textinput form-control', 'pattern': '[a-zA-Z\s]{1,50}', 'title': 'Alphabets and Spaces only'})
        self.fields['phone'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '10', 'pattern': '[0-9]{10}', 'title': 'Numbers only'})
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['gstin'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '15', 'pattern': '[A-Z0-9]{15}',
             'title': 'GSTIN Format Required'})

    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'address', 'email', 'gstin']
        widgets = {
            'address': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '4'
                    }
                )
            }


# form used to get customer details
class SaleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'textinput form-control', 'pattern': '[a-zA-Z\s]{1,50}', 'title': 'Alphabets and Spaces only',
             })
        self.fields['phone'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '10', 'pattern': '[0-9]{10}', 'title': 'Numbers only',
             })
        self.fields['email'].widget.attrs.update({'class': 'textinput form-control'})
        self.fields['gstin'].widget.attrs.update(
            {'class': 'textinput form-control', 'maxlength': '15', 'pattern': '[A-Z0-9]{15}',
             'title': 'GSTIN Format Required'})

    class Meta:
        model = SaleBill
        fields = ['name', 'phone', 'address', 'email', 'gstin']
        widgets = {
            'address': forms.Textarea(
                attrs={
                    'class': 'textinput form-control',
                    'rows': '4'
                    }
                )
            }


# form used to render a single stock item form
class SaleItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.filter(is_deleted=False)
        self.fields['stock'].widget.attrs.update({'class': 'textinput form-control setprice stock', 'required': 'true'})
        self.fields['quantity'].widget.attrs.update(
            {'class': 'textinput form-control setprice quantity', 'min': '0', 'required': 'true'})
        self.fields['perprice'].widget.attrs.update(
            {'class': 'textinput form-control setprice price', 'min': '0', 'required': 'true'})

    class Meta:
        model = SaleItem
        fields = ['stock', 'quantity', 'perprice']


# formset used to render multiple 'SaleItemForm'
SaleItemFormset = formset_factory(SaleItemForm, extra=1)


# form used to accept the other details for sales bill
class SaleDetailsForm(forms.ModelForm):
    class Meta:
        model = SaleBillDetails
        fields = ['eway', 'veh', 'destination', 'po', 'cgst', 'sgst', 'igst', 'cess', 'tcs', 'total']