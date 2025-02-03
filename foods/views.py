from datetime import datetime, timedelta
import json

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils.timezone import make_aware, now, is_naive
from openai import OpenAI
from decouple import config
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from refriges.models import Refrigerator, RefrigeratorAccess
from sigkihan import settings
from .models import DefaultFood, FridgeFood, FoodHistory
from .serializers import DefaultFoodSerializer, FridgeFoodSerializer


today = datetime.today().strftime('%Y-%m-%d')

@extend_schema(
    summary="디폴트 음식 조회",
    description="디폴트 음식 목록을 조회하거나 검색합니다. 검색어를 포함하지 않으면 모든 음식을 반환합니다.",
    tags=["Foods"],
    responses={
        200: {
            "description": "디폴트 음식 목록과 직접 추가하기 이미지 경로",
            "content": {
                "application/json": {
                    "example": {
                        "default_foods": [
                            {"id": 1, "name": "사과", "image": "/media/food_images/apple.png"},
                            {"id": 2, "name": "바나나", "image": "/media/food_images/banana.png"}
                        ],
                        "direct_add_image": "http://your-domain.com/media/default_add_image.svg"
                    }
                }
            }
        }
    }
)
class DefaultFoodListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DefaultFoodSerializer


    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q', '').strip()

        if len(query) >= 1:
            default_foods = DefaultFood.objects.filter(name__icontains=query)
        else:
            default_foods = DefaultFood.objects.all()

        serializer = self.get_serializer(default_foods, many=True)

        # "직접 추가하기" 이미지 URL 생성
        direct_add_image = request.build_absolute_uri('/media/food_images/other.svg')

        # 응답 데이터 구성
        response_data = {
            "default_foods": serializer.data,
            "direct_add_image": direct_add_image
        }

        return Response(response_data, status=200)


class FridgeFoodViewSet(viewsets.ViewSet):
    """
    냉장고 음식 관련 API ViewSet
    """
    permission_classes = [IsAuthenticated]
    # lookup_field = "id"

    @extend_schema(
        summary="내 냉장고 음식 리스트",
        description="사용자의 냉장고에 추가된 모든 음식을 조회합니다.",
        responses={200: FridgeFoodSerializer(many=True)},
        tags = ["Foods"],
    )
    def list(self, request, refrigerator_id=None):
        """
        특정 냉장고의 음식 리스트 조회
        """
        if not refrigerator_id:
            return Response({"error": "Refrigerator ID is required."}, status=400)

        # 사용자가 접근 가능한 냉장고 확인
        refrigerator_access = RefrigeratorAccess.objects.filter(user=request.user, refrigerator_id=refrigerator_id).first()
        if not refrigerator_access:
            return Response({"error": "You do not have access to this refrigerator."}, status=403)

        # 냉장고 음식 조회
        fridge_foods = FridgeFood.objects.filter(refrigerator_id=refrigerator_id).order_by('expiration_date')
        if not fridge_foods.exists():
            return Response({"message": "No foods found in this refrigerator."}, status=404)

        serializer = FridgeFoodSerializer(fridge_foods, many=True, context={'request': request})
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="음식 추가",
        description="냉장고에 기본 제공 음식 또는 사용자 정의 음식을 추가합니다. 디폴트 음식 ID가 없는 경우 사용자 정의 음식을 추가해야 합니다.",
        tags=["Foods"],
        parameters=[
            OpenApiParameter(
                name="refrigerator_id",
                location=OpenApiParameter.PATH,
                description="냉장고 ID",
                required=True,
                type=int,
                examples=[
                    OpenApiExample(
                        name="Refrigerator ID Example",
                        value=1,
                        summary="냉장고 ID",
                        description="음식을 추가할 냉장고 ID"
                    )
                ]
            )
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "default_food_id": {
                        "type": "integer",
                        "example": 1,
                        "description": "디폴트 음식 ID (선택사항)"
                    },
                    "name": {
                        "type": "string",
                        "example": "수박",
                        "description": "사용자 정의 음식 이름 (선택사항, default_food_id가 없는 경우 필수)"
                    },
                    "storage_type": {
                        "type": "string",
                        "enum": ["refrigerated", "frozen", "room_temp"],
                        "example": "refrigerated",
                        "description": "음식 보관 방식 (냉장, 냉동, 실온)"
                    },
                    "purchase_date": {
                        "type": "string",
                        "format": "date",
                        "example": "2024-12-01",
                        "description": "구매 날짜"
                    },
                    "expiration_date": {
                        "type": "string",
                        "format": "date",
                        "example": "2024-12-10",
                        "description": "소비기한"
                    },
                    "quantity": {
                        "type": "integer",
                        "example": 2,
                        "description": "수량"
                    }
                },
                "required": ["purchase_date", "expiration_date", "quantity"]
            }
        },
        responses={
            201: OpenApiResponse(
                description="음식 추가 성공",
                response=FridgeFoodSerializer
            ),
            400: OpenApiResponse(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "error": "Purchase date, expiration date, and quantity are required."
                    }
                }
            ),
            404: OpenApiResponse(
                description="리소스가 존재하지 않음",
                examples={
                    "application/json": {
                        "error": "Refrigerator not found."
                    }
                }
            )
        }
    )
    def create(self, request, refrigerator_id):
        """
        음식 추가
        """
        default_food_id = request.data.get('default_food_id')
        name = request.data.get('name')
        purchase_date = request.data.get('purchase_date')
        expiration_date = request.data.get('expiration_date')
        quantity = request.data.get('quantity')
        storage_type = request.data.get('storage_type')

        if not all([purchase_date, expiration_date, quantity]):
            return Response({"error": "Purchase date, expiration date, and quantity are required."}, status=400)

        refrigerator = Refrigerator.objects.filter(id=refrigerator_id).first()
        if not refrigerator:
            return Response({"error": "Refrigerator not found."}, status=404)

        if default_food_id:
            default_food = DefaultFood.objects.filter(id=default_food_id).first()
            if not default_food:
                return Response({"error": "Default food not found."}, status=404)

            food = FridgeFood.objects.create(
                refrigerator=refrigerator,
                name=name,
                default_food=default_food,
                storage_type=storage_type,
                purchase_date=purchase_date,
                expiration_date=expiration_date,
                quantity=quantity
            )
        else:
            food = FridgeFood.objects.create(
                refrigerator=refrigerator,
                name=name,
                default_food_id=30,
                storage_type=storage_type,
                purchase_date=purchase_date,
                expiration_date=expiration_date,
                quantity=quantity
            )

        serializer = FridgeFoodSerializer(food, context={'request': request})
        return Response(serializer.data, status=201)

    @extend_schema(
        summary="냉장고 음식 수정",
        description="냉장고에 있는 음식을 수정합니다. 디폴트 푸드인 경우 구매일자, 소비기한, 수량만 수정 가능하며, 사용자 정의 푸드인 경우 이름도 수정 가능합니다.",
        tags=["Foods"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "수박", "description": "사용자 정의 음식 이름"},
                    "purchase_date": {"type": "string", "format": "date", "example": "2024-12-01", "description": "구매 날짜"},
                    "expiration_date": {"type": "string", "format": "date", "example": "2024-12-10", "description": "소비기한"},
                    "quantity": {"type": "integer", "example": 2, "description": "수량"}
                }
            }
        },
        responses={200: FridgeFoodSerializer, 404: {"description": "음식 또는 냉장고를 찾을 수 없습니다."}}
    )
    def partial_update(self, request, refrigerator_id=None, id=None):
        """
        냉장고 음식 수정
        """
        food = FridgeFood.objects.filter(refrigerator_id=refrigerator_id, id=id).first()
        if not food:
            return Response({"error": "Food not found."}, status=404)

        if food.default_food.id == 30:
            food.name = request.data.get('name', food.name)
            food.purchase_date = request.data.get('purchase_date', food.purchase_date)
            food.expiration_date = request.data.get('expiration_date', food.expiration_date)
            food.quantity = request.data.get('quantity', food.quantity)
        else:
            food.purchase_date = request.data.get('purchase_date', food.purchase_date)
            food.expiration_date = request.data.get('expiration_date', food.expiration_date)
            food.quantity = request.data.get('quantity', food.quantity)

        food.save()
        serializer = FridgeFoodSerializer(food, context={'request': request})
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="냉장고 음식 삭제",
        description="냉장고에서 특정 음식을 삭제합니다.",
        tags=["Foods"],
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="냉장고 음식의 ID"
            )
        ],
        responses={
            204: {"description": "음식 삭제 성공"},
            404: {"description": "음식 또는 냉장고를 찾을 수 없습니다."}
        }
    )
    def destroy(self, request, refrigerator_id=None, id=None):
        food = FridgeFood.objects.filter(refrigerator_id=refrigerator_id, id=id).first()
        if not food:
            return Response({"error": "Food not found."}, status=404)
        food.delete()
        return Response({"message": "Food deleted successfully."}, status=204)


class FoodHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="음식 소비 또는 폐기 기록 추가",
        description="냉장고에서 특정 음식을 소비하거나 폐기한 기록을 추가합니다.",
        tags=["Foods"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["consumed", "discarded"], "example": "consumed", "description": "행동 유형 (consumed: 먹었어요, discarded: 폐기했어요)"},
                    "quantity": {"type": "integer", "example": 2, "description": "소비 또는 폐기한 수량"},
                },
                "required": ["action", "quantity"]
            }
        },
        responses={
            201: {
                "description": "기록이 성공적으로 추가되었습니다.",
                "content": {
                    "application/json": {
                        "example": {"message": "Consumed recorded successfully.", "remaining_quantity": 3}
                    }
                }
            },
            400: {"description": "잘못된 요청"},
            404: {"description": "음식을 찾을 수 없습니다."}
        },
    )
    def post(self, request, id, refrigerator_id):
        action = request.data.get('action')
        quantity = request.data.get('quantity')

        if not action or not quantity:
            return Response({"error": "Action and quantity are required."}, status=400)

            # 특정 냉장고에 속하는지 확인
        try:
            fridge_food = FridgeFood.objects.get(id=id, refrigerator_id=refrigerator_id)
        except FridgeFood.DoesNotExist:
            raise Http404("Food not found in the specified refrigerator.")

        if action in ['consumed', 'discarded']:
            if fridge_food.quantity < quantity:
                return Response({"error": "Not enough quantity to perform this action."}, status=400)

            FoodHistory.objects.create(
                food_name=fridge_food.name or fridge_food.default_food,
                user=request.user,
                refrigerator=fridge_food.refrigerator,
                fridge_food=fridge_food,
                action=action,
                quantity=quantity
            )

            fridge_food.quantity -= quantity

            if fridge_food.quantity == 0:
                fridge_food.delete()
            else:
                fridge_food.save()

            return Response({
                "message": f"{action.capitalize()} recorded successfully.",
                "remaining_quantity": fridge_food.quantity
            }, status=201)

        return Response({"error": "Invalid action."}, status=400)


class MonthlyTopConsumedFoodView(APIView):
    """
    월간 소비 식품 Top5
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="월간 소비 식품 Top 5",
        description="특정 냉장고에서 월간 소비량이 가장 많은 상위 5개 식품을 반환합니다.",
        tags=["Food Statistics"],
        responses={
            200: {
                "application/json": {
                    "monthly_top_consumed_foods": [
                        {"food_name": "사과", "total_quantity": 10},
                        {"food_name": "바나나", "total_quantity": 8},
                    ]
                }
            },
            404: {"description": "냉장고를 찾을 수 없음"},
        },
    )
    def get(self, request, refrigerator_id):
        # 냉장고 확인
        refrigerator = get_object_or_404(Refrigerator, id=refrigerator_id)

        # 사용자가 냉장고 접근 권한 확인
        if not refrigerator.access_list.filter(user=request.user).exists():
            return Response({"error": "You do not have access to this refrigerator."}, status=403)

        # 이번 달의 시작과 끝 날짜를 timezone-aware로 생성
        now = datetime.now()
        start_of_month = make_aware(datetime(now.year, now.month, 1))
        end_of_month = make_aware(datetime(now.year, now.month + 1, 1))

        # 월간 소비된 식품 조회
        consumed_foods = (
            FoodHistory.objects.filter(
                refrigerator=refrigerator,
                action="consumed",
                timestamp__range=(start_of_month, end_of_month),
            )
            .values("food_name")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

        # 결과 데이터 구조화
        data = {
            "refrigerator": {"id": refrigerator.id, "name": refrigerator.name},
            "monthly_top_consumed_foods": list(consumed_foods),  # 소비된 항목 리스트
        }

        return Response(data, status=200)


class MonthlyConsumptionRankingView(APIView):
    """
    월간 소비 랭킹
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="월간 소비 랭킹",
        description=(
            "특정 냉장고에서 구성원의 월간 소비량을 랭킹 순으로 반환합니다. "
        ),
        tags=["Food Statistics"],
        parameters=[
            OpenApiParameter(
                name="refrigerator_id",
                location=OpenApiParameter.PATH,
                description="냉장고 ID",
                required=True,
                type=int,
                examples=[
                    OpenApiExample(
                        name="냉장고 예시 ID",
                        value=3,
                        description="소비 랭킹을 조회할 냉장고의 ID입니다."
                    )
                ]
            ),
            OpenApiParameter(
                name="month",
                location=OpenApiParameter.QUERY,
                description="조회할 달 (기본값: 현재 달)",
                required=False,
                type=int,
                examples=[
                    OpenApiExample(
                        name="예시: 1월",
                        value=1,
                        description="1월 데이터를 조회할 경우"
                    )
                ]
            ),
            OpenApiParameter(
                name="year",
                location=OpenApiParameter.QUERY,
                description="조회할 연도 (기본값: 현재 연도)",
                required=False,
                type=int,
                examples=[
                    OpenApiExample(
                        name="예시: 2025년",
                        value=2025,
                        description="2025년 데이터를 조회할 경우"
                    )
                ]
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="소비 랭킹 반환 성공",
                examples={
                    "application/json": {
                        "refrigerator": {"id": 3, "name": "우리집 냉장고"},
                        "consumption_ranking": [
                            {
                                "user": {
                                    "id": 1,
                                    "name": "홍길동",
                                    "profile_image": "https://example.com/profile_image_1.jpg"
                                },
                                "total_quantity": 35
                            },
                            {
                                "user": {
                                    "id": 2,
                                    "name": "김철수",
                                    "profile_image": "https://example.com/profile_image_2.jpg"
                                },
                                "total_quantity": 20
                            }
                        ]
                    }
                }
            ),
            403: OpenApiResponse(
                description="구성원이 2명 미만인 경우",
                examples={
                    "application/json": {
                        "error": "구성원이 2명 이상인 경우에만 랭킹이 표시됩니다."
                    }
                }
            ),
            404: OpenApiResponse(
                description="냉장고를 찾을 수 없음",
                examples={
                    "application/json": {
                        "error": "Refrigerator not found."
                    }
                }
            )
        }
    )
    def get(self, request, refrigerator_id):
        # 냉장고 확인
        refrigerator = get_object_or_404(Refrigerator, id=refrigerator_id)

        # 냉장고 접근 권한 확인
        if not refrigerator.access_list.filter(user=request.user).exists():
            return Response({"error": "You do not have access to this refrigerator."}, status=403)

        # 현재 달 또는 요청된 달 계산
        current_time = now()
        month = int(request.query_params.get("month", current_time.month))
        year = int(request.query_params.get("year", current_time.year))

        start_date = datetime(year=year, month=month, day=1)
        end_date = (start_date + relativedelta(months=1))

        # 타임존 어웨어 처리
        if is_naive(start_date):
            start_date = make_aware(start_date)
        if is_naive(end_date):
            end_date = make_aware(end_date)

        # 월간 소비 데이터
        consumption_data = (
            FoodHistory.objects.filter(
                refrigerator=refrigerator,
                action="consumed",
                timestamp__range=(start_date, end_date),
            )
            .values("user__id", "user__name", "user__image")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")
        )

        # 결과 데이터 구조화
        data = {
            "refrigerator": {"id": refrigerator.id, "name": refrigerator.name},
            "consumption_ranking": [
                {
                    "user": {
                        "id": entry["user__id"],
                        "name": entry["user__name"],
                        "image": entry["user__image"] if entry["user__image"] else None
                    },
                    "total_quantity": entry["total_quantity"],
                }
                for entry in consumption_data
            ],
        }

        return Response(data, status=200)


class FoodExpirationQueryView(APIView):

    permission_classes = [IsAuthenticated]
    client = OpenAI(api_key=config("OPENAI_API_KEY"))  # 클라이언트 생성

    @extend_schema(
        summary="식품 소비기한 조회",
        description="ChatGPT를 사용하여 특정 식품의 소비기한 정보를 YYYY-MM-DD 형식으로 반환합니다.",
        tags=["Openai"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "조회할 식품의 이름",
                        "example": "Milk"
                    },
                    "purchase_date": {
                        "type": "string",
                        "format": "date",
                        "description": "제조일자 (YYYY-MM-DD 형식)",
                        "example": "2025-02-02"
                    }
                },
                "required": ["name", "purchase_date"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "food_name": {
                        "type": "string",
                        "description": "조회된 식품 이름",
                        "example": "Milk"
                    },
                    "expiration": {
                        "type": "string",
                        "format": "date",
                        "description": "ChatGPT로부터 받은 소비기한 정보 (YYYY-MM-DD 형식)",
                        "example": "2025-01-20"
                    },
                },
            },
            400: {
                "description": "필수 입력값이 누락된 경우",
                "content": {
                    "application/json": {
                        "example": {"error": "Food name is required."}
                    }
                },
            },
            500: {
                "description": "ChatGPT API 호출 중 오류 발생",
                "content": {
                    "application/json": {
                        "example": {"error": "Failed to fetch expiration info: API timeout"}
                    }
                },
            },
        },
    )
    def post(self, request):
        """
        ChatGPT를 사용하여 식품의 유통기한 정보를 가져오는 API
        """
        # 클라이언트로부터 식품 이름 가져오기
        food_name = request.data.get('name')
        purchase_date = request.data.get('purchase_date')

        if not food_name:
            return Response({"error": "Food name is required."}, status=400)

        # ChatGPT API 호출
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "당신은 식품 소비기한 전문가입니다. "
                            "소비기한을 계산하여 반드시 'YYYY-MM-DD' 형식으로만 답변하세요. "
                            "어떠한 추가적인 문장이나 설명 없이 날짜만 출력하세요."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"""
                            소비기한을 계산하여 'YYYY-MM-DD' 형식으로만 답변해주세요.

                            제품명: {food_name}
                            제조일자: {purchase_date}
                            소비기한을 계산해주세요.
                        """
                    }
                ]
            )

            # ChatGPT의 응답에서 유통기한 정보 추출
            expiration = completion.choices[0].message.content

            return Response({
                "food_name": food_name,
                "expiration": expiration
            }, status=200)

        except Exception as e:
            return Response({"error": f"Failed to fetch expiration info: {str(e)}"}, status=500)


class RecipeRecommendationView(APIView):
    """레시피 추천 API"""
    permission_classes = [IsAuthenticated]
    client = OpenAI(api_key=config("OPENAI_API_KEY"))

    def get_ingredients_info(self, refrigerator):
        """냉장고의 재료 정보 조회 - 재료명만 추출"""
        fridge_foods = (
            FridgeFood.objects.filter(refrigerator=refrigerator)
            .values_list('name', flat=True)
            .distinct()
        )
        
        # 냉장고 재료에서 None이나 빈 문자열 제거
        valid_ingredients = {food for food in fridge_foods if food}
        all_ingredients = valid_ingredients
        
        return all_ingredients

    def check_available_ingredients(self, recipe_ingredients, available_ingredients):
        """레시피 재료와 냉장고 재료를 매칭하여 있는/없는 재료 구분"""
        recipe_ingredients_set = set(recipe_ingredients)
        available = recipe_ingredients_set.intersection(available_ingredients)
        missing = recipe_ingredients_set - available_ingredients

        return list(available), list(missing)

    @extend_schema(
        summary="레시피 추천",
        description="냉장고에 있는 재료를 기반으로 레시피를 추천합니다.",
        tags=["Openai"],
        parameters=[
            OpenApiParameter(
                name="refrigerator_id",
                location=OpenApiParameter.PATH,
                description="냉장고 ID",
                required=True,
                type=int,
                examples=[
                    OpenApiExample(
                        name="냉장고 ID",
                        value=3,
                        description="레시피를 추천받을 냉장고 ID"
                    )
                ]
            ),
            OpenApiParameter(
                name="main_ingredient",
                location=OpenApiParameter.QUERY,
                description="메인 재료",
                required=True,
                type=str,
                examples=[
                    OpenApiExample(
                        name="메인 재료",
                        value="소고기",
                        description="레시피의 메인 재료"
                    )
                ]
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="레시피 추천 성공",
                examples={
                    "application/json": {
                        "recipes": [
                            {
                                "title": "소고기 감자볶음",
                                "total_ingredients": [
                                    "소고기", "감자", "양파", "마늘", "소금", "후추", "식용유"
                                ],
                                "available_ingredients": [
                                    "소고기", "감자", "양파", "마늘"
                                ],
                                "missing_ingredients": [],
                                "cooking_steps": [
                                    "1. 소고기는 핏물을 제거하고 적당한 크기로 썰어주세요.",
                                    "2. 감자, 양파는 한입 크기로 썰어주세요.",
                                    "3. 팬을 달군 후 소고기를 먼저 볶아주세요.",
                                    "4. 감자, 양파를 넣고 함께 볶아주세요.",
                                    "5. 마늘을 넣고 간을 맞춰주세요."
                                ]
                            }
                        ]
                    }
                }
            ),
            400: OpenApiResponse(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "error": "Main ingredient is required."
                    }
                }
            ),
            403: OpenApiResponse(
                description="접근 권한 없음",
                examples={
                    "application/json": {
                        "error": "You do not have access to this refrigerator."
                    }
                }
            ),
            404: OpenApiResponse(
                description="냉장고를 찾을 수 없음",
                examples={
                    "application/json": {
                        "error": "Refrigerator not found."
                    }
                }
            ),
            500: OpenApiResponse(
                description="서버 오류",
                examples={
                    "application/json": {
                        "error": "Failed to get recipe recommendations: API error"
                    }
                }
            )
        }
    )
    def get(self, request, refrigerator_id):
        refrigerator = get_object_or_404(Refrigerator, id=refrigerator_id)
        if not refrigerator.access_list.filter(user=request.user).exists():
            return Response({"error": "You do not have access to this refrigerator."}, status=403)

        main_ingredient = request.query_params.get("main_ingredient")
        if not main_ingredient:
            return Response({"error": "Main ingredient is required."}, status=400)

        available_ingredients = self.get_ingredients_info(refrigerator)
        
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "당신은 요리 전문가입니다. "
                            "주어진 재료로 만들 수 있는 요리 3개를 추천해주세요. "
                            "재료의 양이나 수량은 언급하지 말고 재료명만 나열해주세요."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"메인 재료 '{main_ingredient}'로 "
                            f"만들 수 있는 요리 3개를 추천해주세요.\n"
                            f"다음 JSON 형식으로 응답해주세요:\n"
                            "{\n"
                            "  'recipes': [\n"
                            "    {\n"
                            "      'title': '요리명',\n"
                            "      'ingredients': ['재료1', '재료2', ...],\n"
                            "      'cooking_steps': ['1. 첫번째 단계', '2. 두번째 단계', ...]\n"
                            "    }\n"
                            "  ]\n"
                            "}"
                        )
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={ "type": "json_object" }
            )

            recipes_data = json.loads(completion.choices[0].message.content)
            # 각 레시피에 대해 있는/없는 재료 구분
            for recipe in recipes_data['recipes']:
                available, missing = self.check_available_ingredients(
                    recipe['ingredients'], 
                    available_ingredients
                )
                recipe['available_ingredients'] = sorted(available)  # 정렬하여 보기 좋게
                recipe['missing_ingredients'] = sorted(missing)      # 정렬하여 보기 좋게

            return Response({
                "main_ingredient": main_ingredient,
                "recipes": recipes_data['recipes']
            }, status=200)

        except Exception as e:
            return Response(
                {"error": f"Failed to get recipe recommendations: {str(e)}"}, 
                status=500
            )