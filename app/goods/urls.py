from django.urls import path
from django.views.generic import TemplateView
from .views import CatalogView, ProductView, CatalogAPIView


urlpatterns = [
    
    # Товары
    path('catalog/', CatalogView.as_view(template_name="frontend/catalog.html")),
    path('catalog/<int:id>/', CatalogView.as_view(template_name="frontend/catalog.html")),
    path('product/<int:id>/', ProductView.as_view(template_name="frontend/product.html")),
    path('sale/', TemplateView.as_view(template_name="frontend/sale.html")),
    
    # Заказы
    path('history-order/', TemplateView.as_view(template_name="frontend/historyorder.html")),
    path('order-detail/<int:id>/', TemplateView.as_view(template_name="frontend/oneorder.html")),
    path('orders/<int:id>/', TemplateView.as_view(template_name="frontend/order.html")),
    
    
]
