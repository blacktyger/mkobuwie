from django.contrib.auth.models import User
from decimal import Decimal as d
from django.utils import timezone
from inventory.models import *
from django.db import models

VAT = [('0', 0), ('8', 8), ('19', 19), ('21', 21)]


class Transakcja(models.Model):
    czas = models.DateTimeField(auto_now=True)
    cena = models.DecimalField(default=1, decimal_places=2, max_digits=8)
    ilosc = models.IntegerField(default=1)
    rabat = models.DecimalField(default=0, blank=True, null=True, decimal_places=2, max_digits=8)
    uwagi = models.TextField(default='', blank=True, null=True)
    wartosc = models.DecimalField(default=1, blank=True, null=True, decimal_places=2, max_digits=8)
    vat_procent = models.CharField(choices=VAT, max_length=64, default=VAT[0])
    vat_wartosc = models.DecimalField(default=0, blank=True, null=True, decimal_places=2, max_digits=8)
    produkt = models.ForeignKey(Stock, blank=True, on_delete=models.CASCADE)
    rachunek = models.ForeignKey('Rachunek', blank=True, null=True, on_delete=models.CASCADE)

    def check_sell(self):
        if self.produkt.ilosc < self.ilosc:
            print(f"ZA MALO ({self.produkt.ilosc}szt) {self.produkt.nazwa} NA STANIE!")
            return False
        else:
            return True

    def update_stock(self):
        if self.check_sell():
            print(f"MAGAZYN:{self.produkt.ilosc} MINUS ZAKUP :{self.ilosc}")
            self.produkt.ilosc = self.produkt.ilosc - self.ilosc
            if self.produkt.ilosc < 0:
                print(f"({self.produkt.ilosc}szt) {self.produkt.nazwa} NA STANIE - COS NIE TAK")
                return False
            else:
                print(f"{self.produkt.ilosc} SZTUK {self.produkt.nazwa} - MAGAZYN UAKTUALNIONY")
                self.produkt.save()
                return True

    def save(self, *args, **kwargs):
        self.wartosc = d(self.ilosc * self.cena)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Sprzedaż z dnia {self.czas}"


class Rachunek(models.Model):
    czas = models.DateTimeField(auto_now=True)
    komentarz = models.TextField(blank=True, null=True)
    wartosc = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=8)

    def save(self, *args, **kwargs):
        self.wartosc = sum([item.wartosc for item in self.transakcja_set.all()])
        return super().save(*args, **kwargs)

    def produkty(self):
        return Transakcja.objects.filter(rachunek=self)

    def __str__(self):
        return f"Rachunek  {self.id}"


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12, unique=True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, unique=True)
    gstin = models.CharField(max_length=15, unique=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# contains the purchase bills made
class PurchaseBill(models.Model):
    time = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE,
                                 related_name='purchasesupplier')

    def __str__(self):
        return "Bill no: " + str(self.billno)

    def get_items_list(self):
        return PurchaseItem.objects.filter(billno=self)

    def get_total_price(self):
        purchaseitems = PurchaseItem.objects.filter(billno=self)
        total = 0
        for item in purchaseitems:
            total += item.totalprice
        return total


# contains the purchase stocks made
class PurchaseItem(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchasebillno')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='purchaseitem')
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)

    def __str__(self):
        return "Bill no: " + str(self.billno.billno) + ", Item = " + self.stock.name


# contains the other details in the purchases bill
class PurchaseBillDetails(models.Model):
    billno = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE, related_name='purchasedetailsbillno')

    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)

    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "Bill no: " + str(self.billno.billno)


# contains the sale bills made
class SaleBill(models.Model):
    time = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    gstin = models.CharField(max_length=15)

    def __str__(self):
        return "Bill no: " + str(self.billno)

    def get_items_list(self):
        return SaleItem.objects.filter(billno=self)

    def get_total_price(self):
        saleitems = SaleItem.objects.filter(billno=self)
        total = 0
        for item in saleitems:
            total += item.totalprice
        return total


# contains the sale stocks made
class SaleItem(models.Model):
    data = models.DateTimeField(auto_now=True)
    cena = models.FloatField(default=1)
    ilosc = models.IntegerField(default=1)
    rabat = models.FloatField(default=1)
    uwagi = models.TextField(default=1)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='saleitem')
    sprzedawca = models.ForeignKey(User, default=0, on_delete=models.CASCADE)

    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name='salebillno')
    quantity = models.IntegerField(default=1)
    perprice = models.IntegerField(default=1)
    totalprice = models.IntegerField(default=1)

    def __str__(self):
        return f"Sprzedaż z dnia {self.data} przez {str(self.sprzedawca).capitalize()}"


# contains the other details in the sales bill
class SaleBillDetails(models.Model):
    billno = models.ForeignKey(SaleBill, on_delete=models.CASCADE, related_name='saledetailsbillno')

    eway = models.CharField(max_length=50, blank=True, null=True)
    veh = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    po = models.CharField(max_length=50, blank=True, null=True)

    cgst = models.CharField(max_length=50, blank=True, null=True)
    sgst = models.CharField(max_length=50, blank=True, null=True)
    igst = models.CharField(max_length=50, blank=True, null=True)
    cess = models.CharField(max_length=50, blank=True, null=True)
    tcs = models.CharField(max_length=50, blank=True, null=True)
    total = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "Bill no: " + str(self.billno.billno)
