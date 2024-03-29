import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    View,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    )
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import (
    SelectSupplierForm,
    PurchaseItemFormset,
    PurchaseDetailsForm,
    SupplierForm,
    SaleForm,
    SaleItemFormset,
    SaleDetailsForm,
    TransakcjaForm
    )
from inventory.models import *
from .models import *


class RachunekView(SuccessMessageMixin, View):
    model = Rachunek
    template_name = "bill/sale_bill.html"

    def get(self, request, pk):
        context = {
            'rachunek': Rachunek.objects.get(id=pk),
            'dane': Faktura.objects.get(rachunek__id=pk)
            }
        return render(request, self.template_name, context)


class ZamknijRachunekView(SuccessMessageMixin, View):
    model = Rachunek
    template_name = "sales/sales_list.html"

    def get(self, request, pk):
        rachunek = Rachunek.objects.get(id=pk)
        messages.success(request, f"FAKTURA NR. {rachunek.id} zakończona".upper())
        if 'rachunek' in request.session.keys():
            del request.session['rachunek']
        return redirect('transactions-list')


class FakturaDaneView(SuccessMessageMixin, View):
    model = Faktura
    template_name = "sales/faktura_dane.html"

    def get(self, request, pk):
        rachunek = Rachunek.objects.get(id=pk)
        context = {
            'rachunek': Rachunek.objects.get(id=pk),
            }
        try:
            context['nastepna_faktura'] = Faktura.objects.last().numer_faktury + 1
        except:
            context['nastepna_faktura'] = 1
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        data = request.POST.dict()
        rachunek = Rachunek.objects.get(id=kwargs['pk'])
        del data['csrfmiddlewaretoken']
        print(data)
        data['rachunek'] = rachunek
        if 'konto' in data:
            data['konto'] = True
        else:
            data['konto'] = False
        fv = Faktura.objects.filter(rachunek=rachunek)
        if fv:
            fv.update(**data)
        else:
            Faktura.objects.create(**data)
        return redirect('rachunek', pk=kwargs['pk'])


class FakturaView(SuccessMessageMixin, ListView):
    model = Faktura
    template_name = "bill/bill_list.html"
    context_object_name = 'faktury'
    ordering = ['-data']
    paginate_by = 50


class TransakcjaView(SuccessMessageMixin, ListView):
    model = Rachunek
    context_object_name = 'rachunki'
    template_name = "sales/sales_list.html"
    ordering = ['-czas']
    paginate_by = 50

    def get_context_data(self, *args, **kwargs):
        context = super(TransakcjaView, self).get_context_data(**kwargs)
        today = datetime.date.today()
        year, week_num, day_of_week = today.isocalendar()
        tygodniowa = today - datetime.timedelta(days=7)

        sprzedaz_dzienna = self.model.objects.filter(czas__gte=today)
        sprzedaz_tygodniowa = self.model.objects.filter(czas__week=week_num)

        # context['produkty'] = Transakcja.objects.filter(rachunek=)
        context['sprzedaz_dzienna'] = sum([tx.wartosc for tx in sprzedaz_dzienna])
        context['sprzedaz_tygodniowa'] = sum([tx.wartosc for tx in sprzedaz_tygodniowa])
        return context


class TransakcjaDetailView(SuccessMessageMixin, View):
    model = Transakcja
    form_class = TransakcjaForm
    template_name = "sales/new_sale.html"

    def get(self, request, pk):
        now = datetime.datetime.now()
        numer_produktu = pk

        if Stock.objects.filter(numer_produktu=numer_produktu).exists():
            produkt = Stock.objects.get(numer_produktu=pk)
            initials = {
                'produkt': produkt,
                'cena': produkt.cena,
                'ilosc': 1,
                }
            form = TransakcjaForm(initial=initials)
        else:
            messages.warning(request, message='NIE ZNALEZIONO PRODUKTU')
            return redirect('inventory')

        context = {
            'now': now,
            'produkt': produkt,
            'form': form,
            'x': [x.value() for x in form]
            }
        return render(request, 'sales/new_sale.html', context)

    def post(self, request, *args, **kwargs):
        form = TransakcjaForm(request.POST)
        try:
            form.save(commit=False)
        except:
            print(form.errors)
            print(form.cleaned_data)

        if form.is_valid():
            produkt_id = request.POST.get('numer_produktu')
            produkt = Stock.objects.get(numer_produktu=produkt_id)
            data = form.cleaned_data
            data['czas'] = timezone.now()
            data['produkt'] = produkt
            data['wartosc'] = d(data['ilosc']) * d(data['cena'])
            this = Transakcja(**data)
            print(data)

            if this.update_stock():
                if 'rachunek' not in request.session.keys():
                    rachunek = Rachunek.objects.create()
                    request.session['rachunek'] = rachunek.id
                else:
                    id = request.session['rachunek']
                    rachunek = Rachunek.objects.get(id=id)

                this.rachunek = rachunek
                this.save()
                rachunek.wartosc += this.wartosc
                rachunek.save()
                print(f"SAVED {this} to {rachunek}")
                messages.success(request, f"DODANO DO FAKTURY {produkt.nazwa}")
                return redirect('home')
            else:
                messages.warning(request, f"NIEUDANA SPRZEDAŻ {produkt.nazwa}")
                messages.warning(request, f"ZLECENIE NA {data['ilosc']} SZT | STAN MAGAZYNU {produkt.ilosc}")
                return redirect('edit-stock', numer_produktu=produkt.numer_produktu)
        else:
            messages.warning(request, f"NIE UDAŁO SIĘ SPRZEDAĆ")
            return redirect('edit-stock', numer_produktu=kwargs['numer_produktu'])


# shows a lists of all suppliers
class SupplierListView(ListView):
    model = Supplier
    template_name = "suppliers/suppliers_list.html"
    queryset = Supplier.objects.filter(is_deleted=False)
    paginate_by = 50


# used to add a new supplier
class SupplierCreateView(SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier has been created successfully"
    template_name = "suppliers/edit_supplier.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'New Supplier'
        context["savebtn"] = 'Add Supplier'
        return context


# used to update a supplier's info
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = '/transactions/suppliers'
    success_message = "Supplier details has been updated successfully"
    template_name = "suppliers/edit_supplier.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Edit Supplier'
        context["savebtn"] = 'Save Changes'
        context["delbtn"] = 'Delete Supplier'
        return context


# used to delete a supplier
class SupplierDeleteView(View):
    template_name = "suppliers/delete_supplier.html"
    success_message = "Supplier has been deleted successfully"

    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        return render(request, self.template_name, {'object': supplier})

    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        supplier.is_deleted = True
        supplier.save()
        messages.success(request, self.success_message)
        return redirect('suppliers-list')


# used to view a supplier's profile
class SupplierView(View):
    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 50)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier': supplierobj,
            'bills': bills
            }
        return render(request, 'suppliers/supplier.html', context)


# shows the list of bills of all purchases
class PurchaseView(ListView):
    model = PurchaseBill
    template_name = "purchases/purchases_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 50


# used to select the supplier
class SelectSupplierView(View):
    form_class = SelectSupplierForm
    template_name = 'purchases/select_supplier.html'

    def get(self, request, *args, **kwargs):  # loads the form page
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):  # gets selected supplier and redirects to 'PurchaseCreateView' class
        form = self.form_class(request.POST)
        if form.is_valid():
            supplierid = request.POST.get("supplier")
            supplier = get_object_or_404(Supplier, id=supplierid)
            return redirect('new-purchase', supplier.pk)
        return render(request, self.template_name, {'form': form})


# used to generate a bill object and save items
class PurchaseCreateView(View):
    template_name = 'purchases/new_purchase.html'

    def get(self, request, pk):
        formset = PurchaseItemFormset(request.GET or None)  # renders an empty formset
        supplierobj = get_object_or_404(Supplier, pk=pk)  # gets the supplier object
        context = {
            'formset': formset,
            'supplier': supplierobj,
            }  # sends the supplier and formset as context
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST)  # recieves a post method for the formset
        supplierobj = get_object_or_404(Supplier, pk=pk)  # gets the supplier object
        if formset.is_valid():
            # saves bill
            billobj = PurchaseBill(
                supplier=supplierobj)  # a new object of class 'PurchaseBill' is created with supplier field set to 'supplierobj'
            billobj.save()  # saves object into the db
            # create bill details object
            billdetailsobj = PurchaseBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:  # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj  # links the bill object to the items
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)  # gets the item
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity += billitem.quantity  # updates quantity
                # saves bill item and stock
                stock.save()
                billitem.save()
            messages.success(request, "Purchased items have been registered successfully")
            return redirect('purchase-bill', billno=billobj.billno)
        formset = PurchaseItemFormset(request.GET or None)
        context = {
            'formset': formset,
            'supplier': supplierobj
            }
        return render(request, self.template_name, context)


# used to delete a bill object
class PurchaseDeleteView(SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = "purchases/delete_purchase.html"
    success_url = '/transactions/purchases'

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, "Purchase bill has been deleted successfully")
        return super(PurchaseDeleteView, self).delete(*args, **kwargs)


# shows the list of bills of all sales
class SaleView(ListView):
    model = SaleBill
    template_name = "sales/sales_list.html"
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 50


# used to generate a bill object and save items
class SaleCreateView(View):
    template_name = 'sales/new_sale.html'

    def get(self, request):
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)  # renders an empty formset
        stocks = Stock.objects.filter(is_deleted=False)
        context = {
            'form': form,
            'formset': formset,
            'stocks': stocks
            }
        return render(request, self.template_name, context)

    def post(self, request):
        form = SaleForm(request.POST)
        formset = SaleItemFormset(request.POST)  # recieves a post method for the formset
        if form.is_valid() and formset.is_valid():
            # saves bill
            billobj = form.save(commit=False)
            billobj.save()
            # create bill details object
            billdetailsobj = SaleBillDetails(billno=billobj)
            billdetailsobj.save()
            for form in formset:  # for loop to save each individual form as its own object
                # false saves the item and links bill to the item
                billitem = form.save(commit=False)
                billitem.billno = billobj  # links the bill object to the items
                # gets the stock item
                stock = get_object_or_404(Stock, name=billitem.stock.name)
                # calculates the total price
                billitem.totalprice = billitem.perprice * billitem.quantity
                # updates quantity in stock db
                stock.quantity -= billitem.quantity
                # saves bill item and stock
                stock.save()
                billitem.save()
            messages.success(request, "Sold items have been registered successfully")
            return redirect('sale-bill', billno=billobj.billno)
        form = SaleForm(request.GET or None)
        formset = SaleItemFormset(request.GET or None)
        context = {
            'form': form,
            'formset': formset,
            }
        return render(request, self.template_name, context)


# used to delete a bill object
class SaleDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = "sales/delete_sale.html"
    success_url = '/transactions/sales'

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billno=self.object.billno)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.is_deleted == False:
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, "Sale bill has been deleted successfully")
        return super(SaleDeleteView, self).delete(*args, **kwargs)


# used to display the purchase bill object
class PurchaseBillView(View):
    model = PurchaseBill
    template_name = "bill/purchase_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill': PurchaseBill.objects.get(billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno),
            'billdetails': PurchaseBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
            }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = PurchaseDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = PurchaseBillDetails.objects.get(billno=billno)

            billdetailsobj.eway = request.POST.get("eway")
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill': PurchaseBill.objects.get(billno=billno),
            'items': PurchaseItem.objects.filter(billno=billno),
            'billdetails': PurchaseBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
            }
        return render(request, self.template_name, context)


# used to display the sale bill object
class SaleBillView(View):
    model = SaleBill
    template_name = "bill/sale_bill.html"
    bill_base = "bill/bill_base.html"

    def get(self, request, billno):
        context = {
            'bill': SaleBill.objects.get(billno=billno),
            'items': SaleItem.objects.filter(billno=billno),
            'billdetails': SaleBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
            }
        return render(request, self.template_name, context)

    def post(self, request, billno):
        form = SaleDetailsForm(request.POST)
        if form.is_valid():
            billdetailsobj = SaleBillDetails.objects.get(billno=billno)

            billdetailsobj.eway = request.POST.get("eway")
            billdetailsobj.veh = request.POST.get("veh")
            billdetailsobj.destination = request.POST.get("destination")
            billdetailsobj.po = request.POST.get("po")
            billdetailsobj.cgst = request.POST.get("cgst")
            billdetailsobj.sgst = request.POST.get("sgst")
            billdetailsobj.igst = request.POST.get("igst")
            billdetailsobj.cess = request.POST.get("cess")
            billdetailsobj.tcs = request.POST.get("tcs")
            billdetailsobj.total = request.POST.get("total")

            billdetailsobj.save()
            messages.success(request, "Bill details have been modified successfully")
        context = {
            'bill': SaleBill.objects.get(billno=billno),
            'items': SaleItem.objects.filter(billno=billno),
            'billdetails': SaleBillDetails.objects.get(billno=billno),
            'bill_base': self.bill_base,
            }
        return render(request, self.template_name, context)
