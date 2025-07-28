from django.shortcuts import render
from django.http import HttpRequest
from .models import Item


def get_item_page(request: HttpRequest, item_id: int):
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return render(request, 'item.html', {"error": "Item does not exist"})

    return render(request, 'item.html', {"item": item})
