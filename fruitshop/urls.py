from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('', views.ajax_last_transactions, name="ajax_last_transaction")
]
