# django-diplom

The project contains 4 applications
    app
    path('about/', TemplateView.as_view(template_name="frontend/about.html")),
    path('', TemplateView.as_view(template_name="frontend/index.html")),

    goods 
    path('catalog/', CatalogView.as_view(template_name="frontend/catalog.html")),
    path('catalog/<int:id>/', CatalogView.as_view(template_name="frontend/catalog.html")),
    path('product/<int:id>/', ProductView.as_view(template_name="frontend/product.html")),
    path('sale/', TemplateView.as_view(template_name="frontend/sale.html")),

    ordering
    path('cart/', TemplateView.as_view(template_name="frontend/cart.html")),
    path('history-order/', TemplateView.as_view(template_name="frontend/historyorder.html")),
    path('order-detail/<int:id>/', TemplateView.as_view(template_name="frontend/oneorder.html")),
    path('orders/<int:id>/', TemplateView.as_view(template_name="frontend/order.html")),
    path('payment/<int:id>/', TemplateView.as_view(template_name="frontend/payment.html")),
    path('payment-someone/', TemplateView.as_view(template_name="frontend/paymentsomeone.html")),
    path('progress-payment/', TemplateView.as_view(template_name="frontend/progressPayment.html")),
    
    profile
    path('profile/', TemplateView.as_view(template_name="frontend/profile.html")),
    path('sign-in/', TemplateView.as_view(template_name="frontend/signIn.html")),
    path('sign-up/', TemplateView.as_view(template_name="frontend/signUp.html")),