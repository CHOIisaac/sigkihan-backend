import requests
import logging, os

from decouple import config
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.conf import settings

from refriges.models import Refrigerator, RefrigeratorAccess
from users.models import CustomUser
from .serializers import KakaoLoginRequestSerializer, KakaoLoginResponseSerializer


# 로그 디렉토리 설정
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "kakao_login.log")

# 디렉토리가 없으면 생성
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 로거 설정
logger = logging.getLogger("kakao_login")
logger.setLevel(logging.DEBUG)

# FileHandler 추가
file_handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


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
        logger.info("KakaoLoginView POST request initiated")
        code = request.data.get('code')
        if not code:
            logger.error("Authorization code is missing in the request")
            return Response({"error": "Authorization code is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Access Token 요청
            logger.info("Requesting access token from Kakao")
            token_response = requests.post(
                settings.KAKAO_TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'client_id': settings.KAKAO_CLIENT_ID,
                    'redirect_uri': settings.KAKAO_REDIRECT_URI,
                    'code': code,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            logger.debug(f"Kakao token response status: {token_response.status_code}")
            if token_response.status_code != 200:
                logger.error(f"Failed to fetch access token: {token_response.json()}")
                return Response(
                    {
                        "error": "Failed to fetch access token",
                        "details": token_response.json(),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = token_response.json().get('access_token')
            logger.info("Access token fetched successfully")
        except requests.exceptions.RequestException as e:
            logger.critical(f"Error while requesting access token: {str(e)}")
            return Response(
                {"error": "Failed to connect to Kakao API", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # 사용자 정보 요청
            logger.info("Requesting user information from Kakao")
            user_info_response = requests.get(
                settings.KAKAO_USER_INFO_URL,
                headers={'Authorization': f'Bearer {token}'}
            )
            logger.debug(f"Kakao user info response status: {user_info_response.status_code}")
            if user_info_response.status_code != 200:
                logger.error(f"Failed to fetch user info: {user_info_response.json()}")
                return Response(
                    {
                        "error": "Failed to fetch user info",
                        "details": user_info_response.json(),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_info = user_info_response.json()
            logger.info("User information fetched successfully")
        except requests.exceptions.RequestException as e:
            logger.critical(f"Error while requesting user info: {str(e)}")
            return Response(
                {"error": "Failed to connect to Kakao API", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # 사용자 정보 파싱
            kakao_id = user_info.get('id')
            email = user_info.get('kakao_account', {}).get('email')
            nickname = user_info.get('properties', {}).get('nickname')

            logger.info("Attempting to create or retrieve user")
            # 사용자 저장 또는 가져오기
            user, created = CustomUser.objects.get_or_create(
                kakao_id=kakao_id,
                defaults={'email': email, 'name': nickname, 'is_social': True}
            )
            if created:
                logger.info(f"New user created: {user.name}")
                # 새 유저일 경우 기본 냉장고 생성
                refrigerator = Refrigerator.objects.create(
                    name=f"{nickname}의 냉장고",
                    description=""
                )
                RefrigeratorAccess.objects.create(
                    user=user,
                    refrigerator=refrigerator,
                    role='owner'
                )
                logger.info(f"Default refrigerator created for user: {refrigerator.name}")
            else:
                logger.info(f"Existing user retrieved: {user.name}")

            user_refrigerator = RefrigeratorAccess.objects.filter(user=user, role='owner').first()
            refrigerator_id = user_refrigerator.refrigerator.id if user_refrigerator else None

            # JWT 발급
            logger.info("Generating JWT tokens")
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.name,
                    "refrigerator_id": refrigerator_id,
                    "profile_image": {
                        'id': user.image.id,
                        'name': user.image.name,
                        'image_url': user.image.image,
                    },
                },
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.critical(f"Unexpected error during user creation or token generation: {str(e)}")
            return Response(
                {"error": "Internal Server Error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SuperUserLoginView(APIView):
    """
    슈퍼유저 로그인 및 JWT 발급
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="슈퍼유저 로그인",
        description="슈퍼유저 이메일과 비밀번호를 입력하여 JWT를 발급받습니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "admin3@admin.com"},
                    "password": {"type": "string", "example": "admin3"},
                },
                "required": ["email", "password"]
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string", "description": "Access Token"},
                    "refresh": {"type": "string", "description": "Refresh Token"},
                },
            },
            401: {"description": "인증 실패"},
        },
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)
        if user and user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials or not a superuser."}, status=status.HTTP_401_UNAUTHORIZED)