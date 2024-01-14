import stripe
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.utils import json
from django.http import JsonResponse
from .functions import process_gift_picking
from rest_framework import status
import json
from pydantic import ValidationError
from .validators import QuestionnaireAnswers
from django.conf import settings
from django.http import HttpResponse
from .functions import convert_to_cents, fulfill_order
from gift_finder.models import SelectedGift


@api_view(['POST'])
def api_load_response_data(request):
    try:
        questionnaire_answers_json = request.data["_content"]

        # Parse the JSON data into a Python dictionary
        questionnaire_answers = json.loads(questionnaire_answers_json)

        # Validate questionnaire_answers using Pydantic
        try:
            QuestionnaireAnswers(**questionnaire_answers)
            picked_gifts = process_gift_picking(questionnaire_answers)
            return JsonResponse(picked_gifts, status=status.HTTP_200_OK, safe=False)
        except ValidationError as e:
            print("Validation error:", e)
            return JsonResponse({'Validation error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


stripe.api_key = settings.STRIPE_SECRET_KEY


@api_view(['POST'])
def api_create_checkout_session(request):
    try:
        product_data_json = request.data["_content"]

        # Parse the JSON data into a Python dictionary
        product_data = json.loads(product_data_json)

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': convert_to_cents(product_data['price']),
                            'product_data': {
                                'name': product_data['name'],
                                'images': [product_data['image_url'], ]
                            },
                        },
                        'quantity': 1
                    }
                ],
                metadata={
                    'image_url': product_data['image_url'],
                    'name': product_data['name'],
                    'price': product_data['price'],
                    'link': product_data['link']
                },
                mode='payment',
                # success_url=request.build_absolute_uri('/success/'),
                success_url='https://team-2-backend-dn.vercel.app/api/get_gifts/',
                cancel_url=request.build_absolute_uri('/cancel/'),
                automatic_tax={'enabled': False},
            )
        except Exception as e:
            return str(e)
        return JsonResponse({'link': str(checkout_session.url)}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )
        consumption_data = session.get('metadata', {})

        # Fulfill the purchase...
        fulfill_order(consumption_data)

    # Passed signature verification
    return HttpResponse(status=200)


@api_view(['POST'])
def load_choosed_gift(request):
    try:
        choosed_gift = request.data["_content"]
        choosed_gift_dict = json.loads(choosed_gift)
        is_bought = True
        is_selected = True
        stored_gift = SelectedGift(choosed_gift_dict["name"], int(choosed_gift_dict["price"]),
                                   choosed_gift_dict["image_url"], choosed_gift_dict["link"], is_bought, is_selected)
        stored_gift.save()
        return JsonResponse(stored_gift, status=status.HTTP_200_OK, safe=False)
    except Exception as exeption:
        return JsonResponse({'error': str(exeption)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
