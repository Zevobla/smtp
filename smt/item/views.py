from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, JsonResponse
from .models import Item, Order, OrderItem, Discount, Tax
import stripe
import os
import uuid
from typing import List, Dict, Any
from django.db.models import QuerySet
from django.views.decorators.csrf import csrf_exempt


def get_item_page(request: HttpRequest, item_id: int):
    try:
        item = Item.objects.get(pk=item_id)
        # Debugging: Log the item details to verify data
        print(f"Fetched item: {item}")
    except Item.DoesNotExist:
        return render(request, 'item.html', {"error": "Item does not exist"})

    return render(request, 'item.html', {
        "item": item,
    })

def get_order(request: HttpRequest):
    try:
        order_id = request.session.get('order_id')
        if not order_id:
            return render(request, 'order.html', {"error": "No active order found in session"})

        try:
            order = Order.objects.prefetch_related('order_items__item').get(id=order_id)
        except Order.DoesNotExist:
            return render(request, 'order.html', {"error": "No active order found"})

        # Check if order has items
        if not order.order_items.exists():
            return render(request, 'order.html', {"error": "Order is empty. Please add items first."})

        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")

        # Only create payment intent if we have a valid total
        if order.total_price <= 0:
            order.calculate_total_price()

        print(f"Order total price: {order.total_price}")
        print(f"Amount for Stripe (in cents): {int(order.total_price * 100)}")

        items: List[Dict[str, Any]] = [
            {
                "id": str(order_item.item.id),
                "name": order_item.item.name,
                "price": float(order_item.item.price),
                "quantity": order_item.quantity,
            }
            for order_item in order.order_items.all()
        ]
        
        # Get all available taxes for the dropdown
        taxes = Tax.objects.all()
        
        # Get currency from the first item or default to USD
        currency = order.order_items.first().item.currency if order.order_items.exists() else "USD"

        # Prepare template context
        context = {
            "order_id": str(order.id),
            "items": items,
            "total_price": float(order.total_price),
            "currency": currency,
            "discount": order.discount.code if order.discount else None,
            "applied_discount_code": order.discount.code if order.discount else None,
            "tax": order.tax.name if order.tax else None,
            "taxes": taxes,
            "pk": publishable_key
        }

        # Try to create Stripe payment intent
        try:
            # Validate amount is within Stripe limits (max $999,999.99 = 99999999 cents)
            stripe_amount = int(order.total_price * 100)
            if stripe_amount > 99999999:
                context["stripe_error"] = f"Order total ${order.total_price} exceeds maximum allowed amount"
                context["cs"] = ""
            elif stripe_amount < 1:
                context["stripe_error"] = "Order total must be greater than $0.01"
                context["cs"] = ""
            else:
                payment_intent = stripe.PaymentIntent.create(
                    amount=stripe_amount,
                    currency="usd",
                )
                context["cs"] = payment_intent.client_secret
        except Exception as stripe_error:
            print(f"Stripe error: {stripe_error}")
            context["stripe_error"] = f"Payment processing error: {str(stripe_error)}"
            context["cs"] = ""

        return render(request, 'order.html', context)
    except Exception as e:
        print(f"Error in get_order: {str(e)}")
        return render(request, 'order.html', {"error": str(e)})


def add_to_order(request: HttpRequest, item_id: uuid.UUID):
    try:
        item = Item.objects.get(pk=item_id)

        # Use session to track the order
        if 'order_id' not in request.session:
            request.session['order_id'] = str(uuid.uuid4())

        order, created = Order.objects.get_or_create(
            id=request.session['order_id'],
            defaults={"total_price": 0.00},
        )

        # Check if the item is already in the order
        order_item, created = OrderItem.objects.get_or_create(order=order, item=item)
        if not created:
            # Increment the quantity if the item already exists in the order
            order_item.quantity += 1
            order_item.save()

        # Recalculate the total price
        order.calculate_total_price()

        # Synchronize session's order_id with the created order's id
        if created:
            request.session['order_id'] = str(order.id)

        # Debugging: Log current items in the order
        current_items = [order_item.item for order_item in order.order_items.all()]
        print(f"Order {order.id} now contains items: {[item.id for item in current_items]}")

        return JsonResponse({"message": "Item added to order successfully!", "order_id": str(order.id)})
    except Item.DoesNotExist:
        return JsonResponse({"error": "Item does not exist"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def apply_discount(request: HttpRequest):
    if request.method == "POST":
        discount_code = request.POST.get("discount_code")
        if not discount_code:
            return JsonResponse({"error": "Discount code is required"}, status=400)

        order_id = request.session.get("order_id")
        if not order_id:
            return JsonResponse({"error": "No active order found in session"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
            if order.apply_discount_code(discount_code):
                return JsonResponse({"message": "Discount applied successfully!", "total_price": float(order.total_price)})
            else:
                return JsonResponse({"error": "Invalid discount code"}, status=400)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def apply_discount_code(request: HttpRequest, order_id: str | None = None):
    if request.method == "POST":
        code = request.POST.get("discount_code")
        if not code:
            return JsonResponse({"error": "Discount code is required"}, status=400)
        if not order_id:
            order_id = request.session.get("order_id")
            if not order_id:
                return JsonResponse({"error": "No active order found in session"}, status=400)

        order = get_object_or_404(Order, id=order_id)

        if order.apply_discount_code(code):
            return JsonResponse({
                "success": True,
                "total_price": str(order.total_price),
                "discount_code": code
            })
        else:
            return JsonResponse({"success": False, "error": "Invalid discount code."})


@csrf_exempt
def apply_tax(request: HttpRequest):
    if request.method == "POST":
        tax_id = request.POST.get("tax_id")
        
        order_id = request.session.get("order_id")
        if not order_id:
            return JsonResponse({"error": "No active order found in session"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
            tax = Tax.objects.get(id=tax_id) if tax_id and tax_id != "" else None
            order.tax = tax
            order.calculate_total_price()
            return JsonResponse({
                "success": True,
                "total_price": str(order.total_price),
                "tax_name": tax.name if tax else None
            })
        except (Order.DoesNotExist, Tax.DoesNotExist):
            return JsonResponse({"error": "Order or Tax not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def remove_discount_code(request: HttpRequest):
    if request.method == "POST":
        order_id = request.session.get("order_id")
        if not order_id:
            return JsonResponse({"error": "No active order found in session"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
            order.discount = None
            order.calculate_total_price()
            return JsonResponse({
                "success": True,
                "total_price": str(order.total_price)
            })
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def clear_item(request: HttpRequest):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        if not item_id:
            return JsonResponse({"error": "Item ID is required"}, status=400)

        order_id = request.session.get("order_id")
        if not order_id:
            return JsonResponse({"error": "No active order found in session"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
            order_item = OrderItem.objects.get(order=order, item_id=item_id)
            order_item.delete()

            # Recalculate the total price after removing the item
            order.calculate_total_price()

            return JsonResponse({"success": True, "total_price": float(order.total_price)})
        except (Order.DoesNotExist, OrderItem.DoesNotExist):
            return JsonResponse({"error": "Order or Item not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def clear_order(request: HttpRequest):
    if request.method == "POST":
        order_id = request.session.get("order_id")
        if not order_id:
            return JsonResponse({"error": "No active order found in session"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
            # Query and delete all OrderItem objects related to the order
            OrderItem.objects.filter(order=order).delete()

            order.calculate_total_price()  # Recalculate the total price

            return JsonResponse({"success": True, "total_price": float(order.total_price)})
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
