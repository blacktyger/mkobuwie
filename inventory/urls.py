from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'),
    path('new', views.StockCreateView.as_view(), name='new-stock'),
    path('csv/', views.StockListViewCSV, name='csv'),
    path('stock/<numer_produktu>/edit', views.StockUpdateView.as_view(), name='edit-stock'),
    path('stock/<numer_produktu>/delete', views.StockDeleteView.as_view(), name='delete-stock'),
    path('scanner', views.scanner_handler, name='scanner')
    ]