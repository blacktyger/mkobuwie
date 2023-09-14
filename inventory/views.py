import datetime
from decimal import Decimal

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    View,
    CreateView,
    UpdateView, DetailView, ListView
    )
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Stock, KATEGORIE, ExtraNumer
from .forms import StockForm
from django_filters.views import FilterView
from .filters import StockFilter
from djqscsv import render_to_csv_response


def scanner_handler(request):
    if request.method == "GET":
        code = request.GET.get('numer_produktu')
        print(code)
        if Stock.objects.filter(Q(numer_produktu=code)).exists():
            print("found id")
            messages.success(request, f"ZNALEZIONO PRODUKT {code}")
            return redirect(f'edit-stock', numer_produktu=code)

        elif Stock.objects.filter(Q(extra_numer__numer=code)).exists():
            item = Stock.objects.get(extra_numer__numer=code)
            messages.success(request, f"ZNALEZIONO PRODUKT {code}")
            return redirect(f'edit-stock', numer_produktu=item.numer_produktu)

        else:
            print("not id")
            messages.warning(request, f"NIE MOŻNA ZNALEŹĆ PRODUKTU {code}")
            return redirect('inventory')


class AddExtraNumerView(SuccessMessageMixin, View):
    model = ExtraNumer

    def post(self, request, *args, **kwargs):
        kod = request.POST.get('kod')
        stock = Stock.objects.get(numer_produktu=kwargs['pk'])
        print(kod)
        if kod != '':
            item = ExtraNumer.objects.filter(numer=kod)
            if item:
                item[0].stock = stock
                item[0].save()
            else:
                ExtraNumer.objects.create(numer=kod, stock=stock)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class InwentaryzacjaView(FilterView, ListView):
    filterset_class = StockFilter
    queryset = Stock.objects.all()
    template_name = 'inwentaryzacja.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(InwentaryzacjaView, self).get_context_data(**kwargs)
        p = context['paginator']
        p_obj = context['page_obj']
        context['page_sum'] = sum([item.wartosc for item in p_obj.object_list])
        context['total_sum'] = context['page_sum']
        context['rok'] = datetime.datetime.now().year
        context['ilosc_pozycji'] = self.queryset.count()

        if p_obj.number > 1:
            prev = p_obj.previous_page_number()
            if prev > 0:
                for page in range(0, p_obj.number):
                    context['total_sum'] += sum([item.wartosc for item
                                                in p.page(prev).object_list])
        return context


def inwentaryzacja_update(request, pk):
    if request.method == "POST":
        if 'sprawdzono' in request.POST:
            sprawdzono = True
        else:
            sprawdzono = False
        ilosc = Decimal(request.POST.get('ilosc'))
        print(pk, ':', sprawdzono, ilosc)

        item = Stock.objects.filter(numer_produktu=pk)
        if item:
            item[0].sprawdzono = sprawdzono
            item[0].ilosc = ilosc
            item[0].save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def wyczysc_sprawdzono(request):
    if request.method == 'GET':
        for item in Stock.objects.all():
            item.sprawdzono = False
            item.save()
        print(f"zmieniono {Stock.objects.all().count()} pozycji")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


class StockListView(FilterView, ListView):
    filterset_class = StockFilter
    queryset = Stock.objects.all()
    template_name = 'inventory.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(StockListView, self).get_context_data(**kwargs)
        context['all_stock'] = self.get_queryset().count()
        context['all_kategorie'] = len(KATEGORIE)

        self.request.session['qs'] = [item.numer_produktu for item in self.object_list]
        return context


def StockListViewCSV(request):
    if request.session.get('qs'):
        if len(request.session.get('qs')) == Stock.objects.all().count():
            return render_to_csv_response(Stock.objects.all() \
                                          .values('numer_produktu', 'kategoria',
                                                  'nazwa', 'ilosc', 'cena', 'wartosc'))
        else:
            qs = Stock.objects.filter(numer_produktu__in=request.session.get('qs'))
            qs = qs.values('numer_produktu', 'kategoria',
                           'nazwa', 'ilosc', 'cena', 'wartosc')
            return render_to_csv_response(qs)
    messages.warning(request, f"NAJPIERW WYSZUKAJ ŻEBY WYDRUKOWAC")
    return redirect('inventory')


class StockCreateView(SuccessMessageMixin,
                      CreateView):  # createview class to add new stock, mixin used to display message
    model = Stock  # setting 'Stock' model as model
    form_class = StockForm  # setting 'StockForm' form as form
    template_name = "edit_stock.html"  # 'edit_stock.html' used as the template
    success_message = "Dodano nowy produkt"  # displays message when form is submitted
    slug_field = 'numer_produktu'
    slug_url_kwarg = 'numer_produktu'

    def get_context_data(self, **kwargs):  # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nowy produkt'
        context["savebtn"] = 'Dodaj'
        return context

    def get_success_url(self):
        return reverse('edit-stock', kwargs={'numer_produktu': self.object.numer_produktu})


class StockUpdateView(SuccessMessageMixin, UpdateView):  # updateview class to edit stock, mixin used to display message
    model = Stock  # setting 'Stock' model as model
    form_class = StockForm  # setting 'StockForm' form as form
    template_name = "detail_stock.html"  # 'edit_stock.html' used as the template
    success_message = "Zapisano zmiany w produkcie"  # displays message when form is submitted
    slug_field = 'numer_produktu'
    slug_url_kwarg = 'numer_produktu'

    def get_context_data(self, **kwargs):  # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Szczegóły produktu'
        context["savebtn"] = 'Aktualizuj produkt'
        context["delbtn"] = 'Usuń produkt'
        context["produkt"] = self.get_object()
        context['kody'] = ExtraNumer.objects.filter(stock=self.get_object())
        return context


class StockDeleteView(View):  # view class to delete stock
    template_name = "delete_stock.html"  # 'delete_stock.html' used as the template
    success_message = "Usunięto produkt"  # displays message when form is submitted
    slug_field = 'numer_produktu'
    slug_url_kwarg = 'numer_produktu'

    def get(self, request, numer_produktu):
        print(numer_produktu)
        stock = get_object_or_404(Stock, numer_produktu=numer_produktu)
        return render(request, self.template_name, {'object': stock})

    def post(self, request, numer_produktu):
        print(numer_produktu)

        stock = get_object_or_404(Stock, numer_produktu=numer_produktu)
        stock.delete()
        messages.success(request, self.success_message)
        return redirect('inventory')
