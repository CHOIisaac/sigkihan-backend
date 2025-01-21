from django.http import Http404
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import CustomUser, ProfileImage
from .serializers import TestRequestSerializer, UserSerializer, ProfileImageSerializer, UserDetailSerializer, UserUpdateSerializer


class TestAPIView(GenericAPIView):
    serializer_class = TestRequestSerializer
    @extend_schema(
        summary="Test API",
        description="Returns a simple test message",
        tags=["Tests"],
    )
    def get(self, request):
        return Response({"message": "API is working"})


class UserViewSet(RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    """
    사용자 조회, 수정, 삭제를 처리하는 Generic ViewSet
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        """
        요청 작업(action)에 따라 적절한 Serializer를 반환
        """
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'partial_update':
            return UserUpdateSerializer
        return super().get_serializer_class()

    @extend_schema(
        summary="사용자 정보 조회",
        description="특정 사용자의 ID를 기반으로 상세 정보를 조회합니다.",
        tags=["Users"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="사용자 정보 수정",
        description="사용자의 이름과 프로필 이미지를 수정합니다.",
        tags=["Users"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="사용자 삭제",
        description="특정 사용자를 삭제합니다.",
        tags=["Users"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProfileImageViewSet(ListModelMixin, GenericViewSet):
    """
    프로필 이미지 조회 뷰셋
    """
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer
