from rest_framework.decorators import api_view
from rest_framework.utils import json
from django.http import JsonResponse
from .functions import process_gift_picking
from rest_framework import status
import json
from pydantic import ValidationError
from .validators import QuestionnaireAnswers
from django.http import HttpResponse


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

