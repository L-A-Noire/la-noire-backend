from django.db.models import Count, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from crime.models import Case


class CasesCountAPIView(APIView):
    def get(self, request):
        stats = Case.objects.aggregate(
            total_count=Count('id'),
            open_count=Count('id', filter=Q(is_closed=False)),
            closed_count=Count('id', filter=Q(is_closed=True)),
        )

        return Response(stats, status=status.HTTP_200_OK)
