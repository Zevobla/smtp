from django.urls import path
from . import views

urlpatterns = [
    path('item/<uuid:item_id>/', views.get_item_page, name='get_item_page'),
    path('buy/<uuid:item_id>/', views.create_stripe_session, name='create_stripe_session'),
]
