from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


class TestAPIView(APIView):
    @extend_schema(
        summary="Test API",
        description="Returns a simple test message",
    )
    def get(self, request):
        return Response({"message": "API is working"})
# Create your views here.
