"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from goods.views import CatalogAPIView, ProductApiView, tags_api, categories_api, basket_api
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="frontend/index.html")), # доработать
    
    # app
    path('admin/', admin.site.urls),
    path('', include("goods.urls")),
    # path("", include("frontend.urls")),
    
    # API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('api/catalog/', CatalogAPIView.as_view(), name='catalog_api'),
    path('api/product/<int:id>/', ProductApiView.as_view(), name='product_api'),
    path('api/tags', tags_api, name='tags_api'),
    path('api/categories', categories_api, name='categories_api'),
    path('api/basket', basket_api, name='basket_api'),
    
]
