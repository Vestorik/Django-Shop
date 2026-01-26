from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('payment/<int:id>/', TemplateView.as_view(template_name="frontend/payment.html")),
    path('payment-someone/', TemplateView.as_view(template_name="frontend/paymentsomeone.html")),
    path('progress-payment/', TemplateView.as_view(template_name="frontend/progressPayment.html")),
    path('cart/', TemplateView.as_view(template_name="frontend/cart.html")),
]