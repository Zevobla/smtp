from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from .models import Item
import stripe
import os


def get_item_page(request: HttpRequest, item_id: int):
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return render(request, 'item.html', {"error": "Item does not exist"})

    return render(request, 'item.html', {"item": item, "stripe_publishable_key": os.getenv('STRIPE_PUBLISHABLE_KEY')})


def create_stripe_session(request: HttpRequest, item_id: int):
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item does not exist"}, status=404)

    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.name,
                    },
                    'unit_amount': int(item.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=os.getenv('STRIPE_SUCCESS_URL'),
            cancel_url=os.getenv('STRIPE_CANCEL_URL'),
        )
        return JsonResponse({"sessionId": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
