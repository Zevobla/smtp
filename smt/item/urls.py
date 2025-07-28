from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:item_id>/', views.get_item_page, name='get_item_page'),
]
