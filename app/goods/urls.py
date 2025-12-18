from django.urls import include, path
from django.views.generic import TemplateView
from .views import CatalogView, ProductView, ProductApiView, CatalogAPIView


urlpatterns = [
    path('catalog/', CatalogView.as_view(template_name="frontend/catalog.html")),
    path('catalog/<int:id>/', CatalogView.as_view(template_name="frontend/catalog.html")),
    path('product/<int:id>/', ProductView.as_view(template_name="frontend/product.html")),
    path('sale/', TemplateView.as_view(template_name="frontend/sale.html")),
    
]
