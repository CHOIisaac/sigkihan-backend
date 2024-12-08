import requests

from decouple import config
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import KakaoLoginRequestSerializer, KakaoLoginResponseSerializer

# class TestAPIView(GenericAPIView):
#     serializer_class = TestRequestSerializer
#     @extend_schema(
#         summary="Test API",
#         description="Returns a simple test message",
#     )
#     def get(self, request):
#         return Response({"message": "API is working"})


class KakaoLoginView(APIView):

    @extend_schema(
        summary="카카오 로그인",
        description=(
                "카카오 로그인을 위해 프론트엔드에서 받은 authorization_code를 사용하여 "
                "카카오 사용자 정보를 가져오고, JWT 토큰을 발급합니다."
        ),
        request=KakaoLoginRequestSerializer,  # 요청 직렬화기
        responses={200: KakaoLoginResponseSerializer},  # 응답 직렬화기
    )
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({"error": "Authorization code is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Access Token 요청
        token_response = requests.post(
            config('KAKAO_TOKEN_URL'),
            data={
                'grant_type': 'authorization_code',
                'client_id': config('KAKAO_CLIENT_ID'),
                'redirect_uri': config('KAKAO_REDIRECT_URI'),
                'code': code,
            }
        )
        if token_response.status_code != 200:
            return Response({"error": "Failed to fetch access token"}, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_response.json().get('access_token')

        # 사용자 정보 요청
        user_info_response = requests.get(
            config('KAKAO_USER_INFO_URL'),
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if user_info_response.status_code != 200:
            return Response({"error": "Failed to fetch user info"}, status=status.HTTP_400_BAD_REQUEST)

        user_info = user_info_response.json()
        kakao_id = user_info.get('id')
        email = user_info.get('kakao_account', {}).get('email')
        nickname = user_info.get('properties', {}).get('nickname')
        profile_image = user_info.get('properties', {}).get('profile_image')

        # 사용자 저장 또는 가져오기
        user, created = CustomUser.objects.get_or_create(
            kakao_id=kakao_id,
            defaults={'email': email, 'username': nickname, 'profile_image': profile_image}
        )

        # JWT 발급
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "profile_image": user.profile_image.url if user.profile_image else None,
            },
        }, status=status.HTTP_200_OK)



class KakaoLoginRedirectView(APIView):
    @extend_schema(
        summary="카카오 로그인 페이지로 리다이렉트",
        description=(
            "카카오 로그인을 위해 사용자에게 카카오 로그인 페이지로 리다이렉트합니다. "
            "리다이렉트 완료 후, 설정된 `KAKAO_REDIRECT_URI`로 인가 코드가 반환됩니다."
        ),
        responses={302: "카카오 로그인 페이지로 리다이렉트"}
    )
    def get(self, request):
        kakao_login_url = (
            f"https://kauth.kakao.com/oauth/authorize?"
            f"client_id={config('KAKAO_CLIENT_ID')}&"
            f"redirect_uri={config('KAKAO_REDIRECT_URI')}&"
            f"response_type=code"
        )
        return redirect(kakao_login_url)