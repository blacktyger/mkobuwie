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

KATEGORIE = [('obuwie-damskie', 'obuwie-damskie'),
             ('obuwie-meskie', 'obuwie-meskie'),
             ('obuwie-dzieciece', 'obuwie-dzieciece'),
             ('obuwie-mlodziezowe', 'obuwie-mlodziezowe'),
             ('odziez', 'odziez'),
             ('dodatki', 'dodatki'),
             ('torebki', 'torebki'),
             ('bielizna', 'bielizna'),
             ('inne', 'inne')
             ]


def create_product_code():
    previous = Stock.objects.order_by('numer_produktu').last()
    print("===================")
    print(previous.__dict__)

    if previous:
        print('WAS STACK, NEW', int(previous.numer_produktu) + 10)
        return int(previous.numer_produktu) + 10
    else:
        print('DUNNO', int(f"90000010"))
        return int(f"90000010")


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

    class Meta:
        ordering = ['nazwa']

    def save(self, *args, **kwargs):
        self.wartosc = d(self.ilosc * self.cena)
        self.name = self.nazwa

        if not self.numer_produktu:

            EAN = barcode.get_barcode_class('ean8')
            ean = EAN(f'{create_product_code()}', writer=ImageWriter())
            self.numer_produktu = int(str(ean))
            print(self.numer_produktu)

            buffer = BytesIO()
            ean.write(buffer, text=f"{self.numer_produktu},"
                                   f"\n {self.nazwa}")

            self.barcode.save(f'{self.numer_produktu}.png', File(buffer), save=False)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"/inventory/stock/{self.numer_produktu}/edit"

    @classmethod
    def repair_name(cls):
        """ Get rid of extra signs in names"""
        znaki = ('"', '!', "'", "?")
        for item in cls.objects.all():
            if item.nazwa.startswith(znaki):
                for znak in znaki:
                    item.nazwa = item.nazwa.replace(znak, '')
                    item.save()

    def __str__(self):
        return f"[{self.kategoria.upper()}] {self.nazwa}"


# TEST UNIT
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
