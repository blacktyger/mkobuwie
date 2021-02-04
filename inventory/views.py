from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    View,
    CreateView,
    UpdateView, DetailView, ListView
    )
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Stock
from .forms import StockForm
from django_filters.views import FilterView
from .filters import StockFilter


def scanner_handler(request):
    if request.method == "GET":
        code = request.GET.get('numer_produktu')
        print(code)
        if Stock.objects.filter(numer_produktu=code).exists():
            print("found id")
            messages.success(request, f"ZNALEZIONO PRODUKT {code}")
            return redirect(f'edit-stock', pk=code)
        else:
            print("not id")
            messages.warning(request, f"NIE MOŻNA ZNALEŹĆ PRODUKTU {code}")
            return redirect('inventory')


class StockListView(FilterView, ListView):
    filterset_class = StockFilter
    queryset = Stock.objects.filter(is_deleted=False)
    template_name = 'inventory.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(StockListView, self).get_context_data(**kwargs)
        context['all_stock'] = Stock.objects.filter(is_deleted=False).count()
        return context


class StockCreateView(SuccessMessageMixin, CreateView):                                 # createview class to add new stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "edit_stock.html"                                                   # 'edit_stock.html' used as the template
    success_message = "Dodano nowy produkt"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Nowy produkt'
        context["savebtn"] = 'Dodaj'
        return context

    def get_success_url(self):
        return reverse('edit-stock', kwargs={'pk': self.object.pk})


class StockUpdateView(SuccessMessageMixin, UpdateView):                                 # updateview class to edit stock, mixin used to display message
    model = Stock                                                                       # setting 'Stock' model as model
    form_class = StockForm                                                              # setting 'StockForm' form as form
    template_name = "detail_stock.html"                                                   # 'edit_stock.html' used as the template
    success_message = "Zapisano zmiany w produkcie"                             # displays message when form is submitted

    def get_context_data(self, **kwargs):                                               # used to send additional context
        context = super().get_context_data(**kwargs)
        context["title"] = 'Szczegóły produktu'
        context["savebtn"] = 'Aktualizuj produkt'
        context["delbtn"] = 'Usuń produkt'
        context["produkt"] = self.get_object()
        return context


class StockDeleteView(View):                                                            # view class to delete stock
    template_name = "delete_stock.html"                                                 # 'delete_stock.html' used as the template
    success_message = "Usunięto produkt"                             # displays message when form is submitted
    
    def get(self, request, pk):
        print(pk)
        stock = get_object_or_404(Stock, pk=pk)
        return render(request, self.template_name, {'object': stock})

    def post(self, request, pk):
        print(pk)

        stock = get_object_or_404(Stock, pk=pk)
        stock.is_deleted = True
        stock.save()                                               
        messages.success(request, self.success_message)
        return redirect('inventory')