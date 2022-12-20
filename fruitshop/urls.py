from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path("ajax_last_transaction/", views.ajax_last_transactions, name="ajax_last_transaction"),
    path("ajax_money_bank/", views.ajax_money_bank, name="ajax_money_bank"),
    path("upload_declaration/", views.upload_declaration, name="upload_declaration"),

]
