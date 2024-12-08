import requests
import logging, os

from decouple import config
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.conf import settings

from .serializers import KakaoLoginRequestSerializer, KakaoLoginResponseSerializer

# class TestAPIView(GenericAPIView):
#     serializer_class = TestRequestSerializer
#     @extend_schema(
#         summary="Test API",
#         description="Returns a simple test message",
#     )
#     def get(self, request):
#         return Response({"message": "API is working"})



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
            profile_image = user_info.get('properties', {}).get('profile_image')

            logger.info("Attempting to create or retrieve user")
            # 사용자 저장 또는 가져오기
            user, created = CustomUser.objects.get_or_create(
                kakao_id=kakao_id,
                defaults={'email': email, 'username': nickname, 'profile_image': profile_image}
            )
            if created:
                logger.info(f"New user created: {user.username}")
            else:
                logger.info(f"Existing user retrieved: {user.username}")

            # JWT 발급
            logger.info("Generating JWT tokens")
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
        except Exception as e:
            logger.critical(f"Unexpected error during user creation or token generation: {str(e)}")
            return Response(
                {"error": "Internal Server Error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



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