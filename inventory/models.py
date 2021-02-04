import decimal
import random
from io import BytesIO
from time import sleep
from decimal import Decimal as d
import barcode
from barcode.writer import ImageWriter
from django.core.files import File
from django.db import models

from inventory.items import items

KATEGORIE = [('obuwie', 'obuwie'), ('damskie', 'damskie'), ('dzieciece', 'dzieciece')]


def create_product_code(kategoria):
    num = 0
    if kategoria == 'obuwie':
        num = 1
    elif kategoria == "damskie":
        num = 2
    elif kategoria == "dzieciece":
        num = 3
    else:
        num = num

    if Stock.objects.filter(kategoria=kategoria).count() == 0:
        print('No stock: INIT ', int(f"{num}0000010"))
        return int(f"{num}0000010")
    else:
        previous = Stock.objects.filter(kategoria=kategoria).last().numer_produktu
        if previous:
            print('WAS STACK, NEW', int(previous) + 10)
            return int(previous) + 10
        else:
            print('DUNNO', int(f"{num}0000010"))
            return int(f"{num}0000010")


class Stock(models.Model):
    numer_produktu = models.CharField(max_length=128, null=True, unique=True)
    kategoria = models.CharField(choices=KATEGORIE, max_length=64, default=KATEGORIE[0])
    name = models.CharField(max_length=64, blank=True, editable=False)
    nazwa = models.CharField(max_length=64, default="nazwa")
    quantity = models.IntegerField(default=1, null=True, editable=False)
    ilosc = models.IntegerField(default=1, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, null=True, editable=False)
    cena = models.DecimalField(max_digits=8, decimal_places=2, default=0, null=True)
    wartosc = models.DecimalField(max_digits=8, decimal_places=2, default=0, null=True)
    is_deleted = models.BooleanField(default=False, editable=False)
    informacje = models.TextField(blank=True, null=True)
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True, default="")

    def save(self, *args, **kwargs):
        self.wartosc = d(self.ilosc * self.cena)
        self.name = self.nazwa

        if not self.numer_produktu:

            EAN = barcode.get_barcode_class('ean8')
            ean = EAN(f'{create_product_code(self.kategoria)}', writer=ImageWriter())

            self.numer_produktu = int(str(ean))
            self.pk = self.numer_produktu
            print(self.pk)

            buffer = BytesIO()
            ean.write(buffer, text=f"{self.numer_produktu},"
                                   f"\n {self.nazwa}")

            self.barcode.save(f'{self.numer_produktu}.png', File(buffer), save=False)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/inventory/stock/{self.numer_produktu}/edit"

    def __str__(self):
        return f"[{self.kategoria.upper()}] {self.nazwa}"


def add_stock():
    for x in items:
        try:
            cena = d(x[2])
            ilosc = d(x[1])
            nazwa = x[0]
            kategoria = random.choice(KATEGORIE)[1]

            print(cena, kategoria, ilosc)
            create = Stock.objects.get_or_create(nazwa=nazwa,
                                                 ilosc=ilosc, kategoria=kategoria,
                                                 cena=cena)
            print('ADDED ', create[0].numer_produktu)
        except:

            continue

    return f"Done."
