from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('profile/', TemplateView.as_view(template_name="frontend/profile.html")),

    path('sign-in/', TemplateView.as_view(template_name="frontend/signIn.html")),
    path('sign-up/', TemplateView.as_view(template_name="frontend/signUp.html")),
]