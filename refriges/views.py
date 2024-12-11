from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from refriges.models import RefrigeratorAccess, Refrigerator
from refriges.serializers import RefrigeratorSerializer


class RefrigeratorListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RefrigeratorSerializer

    def get(self, request, id=None):
        print(request.user)
        print(id)

        # 현재 사용자가 접근할 수 있는 냉장고 조회
        try:
            refrigerator = Refrigerator.objects.get(id=id)
        except Refrigerator.DoesNotExist:
            return Response({"detail": "Refrigerator not found."}, status=404)

        # 직렬화
        serializer = RefrigeratorSerializer(refrigerator)
        return Response(serializer.data, status=200)