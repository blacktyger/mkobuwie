from .models import Stock, Transakcja, Rachunek, Faktura

from django.apps import apps
from django.contrib import admin

myapp = apps.get_app_config('transactions')


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = myapp.get_models()
for model in models:
    if model in (Transakcja, Rachunek, Faktura):
        admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
        try:
            admin.site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            pass

