import django_filters
from django.db.models import Q

from .models import Stock


class StockFilter(django_filters.FilterSet):
    nazwa = django_filters.CharFilter(lookup_expr='icontains')
    numbers = django_filters.CharFilter(method='any_number')

    def any_number(self, qs, name, value):
        return qs.filter(
            Q(extra_numer__numer=value) | Q(numer_produktu=value))

    class Meta:
        model = Stock
        fields = ['nazwa', 'numbers']
