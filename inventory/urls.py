from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'),
    path('inwentaryzacja', views.InwentaryzacjaView.as_view(), name='inwentaryzacja'),
    path('inwentaryzacja_update/<pk>', views.inwentaryzacja_update, name='inwentaryzacja-update'),
    path('new', views.StockCreateView.as_view(), name='new-stock'),
    path('dodaj_kod/<pk>', views.AddExtraNumerView.as_view(), name='dodaj-kod'),

    path('csv/', views.StockListViewCSV, name='csv'),
    path('stock/<numer_produktu>/edit', views.StockUpdateView.as_view(), name='edit-stock'),
    path('stock/<numer_produktu>/delete', views.StockDeleteView.as_view(), name='delete-stock'),
    path('scanner', views.scanner_handler, name='scanner'),
    path('wyczysc_sprawdzono', views.wyczysc_sprawdzono, name='wyczysc-sprawdzono')
    ]