from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    if isinstance(exc, ValidationError):
        return Response(
            {
                "message": "Veuillez corriger les champs invalides.",
                "errors": response.data,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    return Response(
        {
            "message": detail or "Une erreur est survenue.",
            "errors": response.data if isinstance(response.data, dict) else {"detail": response.data},
        },
        status=response.status_code,
    )
