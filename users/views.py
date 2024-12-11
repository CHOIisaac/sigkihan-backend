from django.http import Http404
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import CustomUser, ProfileImage
from .serializers import TestRequestSerializer, UserSerializer, ProfileImageSerializer


class TestAPIView(GenericAPIView):
    serializer_class = TestRequestSerializer
    @extend_schema(
        summary="Test API",
        description="Returns a simple test message",
    )
    def get(self, request):
        return Response({"message": "API is working"})


class UserDetailAPIView(APIView):
    """
    GET: 특정 사용자 조회
    PUT: 사용자 정보 수정
    """
    serializer_class = UserSerializer
    def get(self, request, id):
        try:
            user = get_object_or_404(CustomUser, pk=id)  # 객체를 조회
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Http404:
            # 객체가 존재하지 않을 경우 처리
            return Response({"error": f"User with ID {id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 그 외 예외 처리
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            print("Request data:", request.data)  # 디버깅용
            user = get_object_or_404(CustomUser, pk=id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)  # 성공 응답
            print("Serializer errors:", serializer.errors)  # 디버깅용
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 유효하지 않은 데이터 응답
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileImageViewSet(ListModelMixin, GenericViewSet):
    """
    프로필 이미지 조회 뷰셋
    """
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer