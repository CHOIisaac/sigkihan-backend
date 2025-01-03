from django.http import Http404
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin
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


class UserDetailAPIView(APIView):
    """
    GET: 특정 사용자 조회
    PUT: 사용자 정보 수정
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(
        summary="사용자 정보 조회",
        description="특정 사용자의 ID를 기반으로 상세 정보를 조회합니다.",
        tags=["Users"],
        parameters=[
            {
                "name": "id",
                "in": "path",
                "required": True,
                "description": "조회할 사용자의 ID",
                "schema": {"type": "integer"}
            }
        ],
        responses={
            200: UserDetailSerializer,
            404: {"description": "사용자를 찾을 수 없음"},
            500: {"description": "예상치 못한 오류 발생"}
        },
    )
    def get(self, request, id):
        try:
            user = get_object_or_404(CustomUser, pk=id)  # 객체를 조회
            serializer = UserDetailSerializer(user)
            return Response(serializer.data)
        except Http404:
            # 객체가 존재하지 않을 경우 처리
            return Response({"error": f"User with ID {id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # 그 외 예외 처리
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="사용자 정보 수정",
        description="사용자의 이름과 프로필 이미지를 수정합니다.",
        tags=["Users"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "새로운 이름", "description": "사용자 이름"},
                    "image_id": {"type": "integer", "example": 3, "description": "ProfileImage ID"}
                },
                "required": ["name", "image_id"]
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "새로운 이름"},
                    "profile_image": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 3},
                            "name": {"type": "string", "example": "프로필 이미지 이름"},
                            "image_url": {"type": "string", "example": "/media/profile_images/image.png"}
                        }
                    }
                }
            }
        }
    )
    def patch(self, request, id):
        try:
            print("Request data:", request.data)  # 디버깅용
            user = get_object_or_404(CustomUser, pk=id)
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)  # 성공 응답
            print("Serializer errors:", serializer.errors)  # 디버깅용
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # 유효하지 않은 데이터 응답
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="사용자 삭제",
        description="특정 사용자를 완전히 삭제합니다. 사용자 ID를 경로 매개변수로 전달해야 합니다.",
        tags=["Users"],
        responses={
            204: {"description": "사용자 삭제 성공"},
            404: {"description": "사용자를 찾을 수 없음"},
            500: {"description": "예상치 못한 오류 발생"}
        },
    )
    def delete(self, request, id):
        """
        DELETE 요청으로 사용자 완전 삭제
        """
        try:
            user = get_object_or_404(CustomUser, pk=id)
            user.delete()
            return Response({"message": f"User with ID {id} has been deleted."}, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({"error": f"User with ID {id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileImageViewSet(ListModelMixin, GenericViewSet):
    """
    프로필 이미지 조회 뷰셋
    """
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer
