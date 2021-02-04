import django_filters
from .models import Stock


class StockFilter(django_filters.FilterSet):
    nazwa = django_filters.CharFilter(lookup_expr='icontains')
    numer_produktu = django_filters.CharFilter(lookup_expr='exact')

    class Meta:
        model = Stock
        fields = ['nazwa', 'numer_produktu']
