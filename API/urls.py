from django.urls import path
from . import views

urlpatterns = [
    path('get_gifts/', views.api_load_response_data),
    path('gifts-archive/', views.load_choosed_gift),
    path('gift_consumption/', views.api_create_checkout_session),
    path('webhooks/stripe/', views.stripe_webhook_view, name='stripe-webhook'),
]
