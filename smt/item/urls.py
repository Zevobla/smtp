from django.urls import path
from . import views

urlpatterns = [
    path('item/<uuid:item_id>/', views.get_item_page, name='get_item_page'),
    path('order/', views.get_order, name='get_order'),
    path('order/<uuid:item_id>/', views.add_to_order, name='add_to_order'),
    path('apply/', views.apply_discount_code, name='apply_discount_code'),
    path('remove-discount/', views.remove_discount_code, name='remove_discount_code'),
    path('apply-tax/', views.apply_tax, name='apply_tax'),
    path('clear-item/', views.clear_item, name='clear_item'),
    path('clear-order/', views.clear_order, name='clear_order'),
]
