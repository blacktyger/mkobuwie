from django.contrib import admin
from .models import Stock

from django.apps import apps
from django.contrib import admin
from django.utils.html import format_html

myapp = apps.get_app_config('inventory')

field_list = ['numer_produktu',
              'kategoria',
              'nazwa',
              'cena',
              'ilosc',
              'wartosc',
              'informacje',
              'barcode',
              ]


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields if field.name in field_list]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = myapp.get_models()

for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass
