from django.urls import path
from . import views

urlpatterns = [
    path('graph_view/', views.graph_view)
]