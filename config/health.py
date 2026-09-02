from django.db import connection, OperationalError
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


def liveness(request):
    """
    Liveness probe — plain Django view, no DRF overhead.

    Confirms the process is alive and the database connection is reachable.
    Returns HTTP 200 {"status": "ok"} or HTTP 503 on DB failure.
    """
    try:
        connection.ensure_connection()
    except OperationalError as exc:
        return JsonResponse(
            {"status": "error", "database": str(exc)},
            status=503,
        )

    return JsonResponse({"status": "ok"})


# Keep the old name as an alias so existing /health route needs no change.
health = liveness


class ReadinessView(APIView):
    """
    Readiness probe — DRF view, same dispatch stack as the real API.

    Bypasses authentication and throttling (AllowAny, no throttle classes)
    so Kubernetes probes work without credentials, but still exercises:
    - Django middleware chain
    - DRF dispatch / content negotiation
    - ORM (lightweight COUNT on the classicmodels_productline table)

    Returns HTTP 200 {"status": "ok"} when ready,
    or HTTP 503 {"status": "error", ...} when not.
    """

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    @extend_schema(exclude=True)
    def get(self, request):
        from classicmodels.models import ProductLine  # local import avoids circular refs

        try:
            ProductLine.objects.count()
        except Exception as exc:  # noqa: BLE001
            return Response(
                {"status": "error", "database": str(exc)},
                status=503,
            )

        return Response({"status": "ok"})
