from django.shortcuts import render
from django.views.generic import View, TemplateView
from transactions.models import *


class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        sprzedane = Transakcja.objects.filter(ilosc__gte=3)
        ilosci = {}
        for item in sprzedane:
            if item.produkt.nazwa in ilosci:
                ilosci[item.produkt.nazwa] += item.ilosc
            else:
                ilosci[item.produkt.nazwa] = item.ilosc

        ilosci = sorted(ilosci.items(), key=lambda x: x[1], reverse=True)[:30]
        context = {
            'labels': [x[0] for x in ilosci],
            'data': [x[1] for x in ilosci],
            }
        return render(request, self.template_name, context)


class AboutView(TemplateView):
    template_name = "about.html"
