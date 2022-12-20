from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path("ajax_last_transaction/", views.ajax_last_transactions, name="ajax_last_transaction"),
]
