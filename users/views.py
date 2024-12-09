from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import TestRequestSerializer


class TestAPIView(GenericAPIView):
    serializer_class = TestRequestSerializer
    @extend_schema(
        summary="Test API",
        description="Returns a simple test message",
    )
    def get(self, request):
        return Response({"message": "API is working"})

