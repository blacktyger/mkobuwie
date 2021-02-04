from django.shortcuts import render
from django.views.generic import View, TemplateView
from transactions.models import Transakcja


class HomeView(View):
    template_name = "home.html"

    def get(self, request):
        sprzedane = Transakcja.objects.all()
        ilosci = {}
        for item in sprzedane:
            if item.produkt.nazwa in ilosci:
                ilosci[item.produkt.nazwa] += item.ilosc
            else:
                ilosci[item.produkt.nazwa] = item.ilosc

        context = {
            'labels': [x for x in ilosci],
            'data': [v for k, v in ilosci.items()],
            }
        return render(request, self.template_name, context)


class AboutView(TemplateView):
    template_name = "about.html"