from openai import OpenAI
from decouple import config
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets

from refriges.models import Refrigerator, RefrigeratorAccess
from .models import DefaultFood, FridgeFood, FoodHistory
from .serializers import DefaultFoodSerializer, FridgeFoodSerializer


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
        description="냉장고에 기본 제공 음식 또는 사용자 정의 음식을 추가합니다.",
        tags=["Foods"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "default_food_id": {"type": "integer", "example": 1, "description": "디폴트 음식 ID"},
                    "name": {"type": "string", "example": "수박", "description": "사용자 정의 음식 이름"},
                    "purchase_date": {"type": "string", "format": "date", "example": "2024-12-01", "description": "구매 날짜"},
                    "expiration_date": {"type": "string", "format": "date", "example": "2024-12-10", "description": "소비기한"},
                    "quantity": {"type": "integer", "example": 2, "description": "수량"}
                },
                "required": ["purchase_date", "expiration_date", "quantity"]
            }
        },
        responses={201: FridgeFoodSerializer, 400: {"description": "잘못된 요청"}}
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
                purchase_date=purchase_date,
                expiration_date=expiration_date,
                quantity=quantity
            )
        else:
            food = FridgeFood.objects.create(
                refrigerator=refrigerator,
                name=name,
                default_food_id=30,
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

        if food.default_food:
            food.purchase_date = request.data.get('purchase_date', food.purchase_date)
            food.expiration_date = request.data.get('expiration_date', food.expiration_date)
            food.quantity = request.data.get('quantity', food.quantity)
        else:
            food.name = request.data.get('name', food.name)
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

            fridge_food.quantity -= quantity

            if fridge_food.quantity == 0:
                fridge_food.delete()
            else:
                fridge_food.save()

            FoodHistory.objects.create(
                food_name=fridge_food.name or fridge_food.default_food,
                user=request.user,
                action=action,
                quantity=quantity
            )

            return Response({
                "message": f"{action.capitalize()} recorded successfully.",
                "remaining_quantity": fridge_food.quantity
            }, status=201)

        return Response({"error": "Invalid action."}, status=400)

    # @extend_schema(
    #     summary="특정 음식에 대한 히스토리 조회",
    #     description="냉장고의 특정 음식에 대한 소비 및 폐기 기록을 조회합니다.",
    #     responses={
    #         200: {
    #             "description": "히스토리 조회 성공",
    #             "content": {
    #                 "application/json": {
    #                     "example": [
    #                         {"action": "consumed", "quantity": 2, "timestamp": "2024-12-11T08:00:00Z"},
    #                         {"action": "discarded", "quantity": 1, "timestamp": "2024-12-12T09:00:00Z"}
    #                     ]
    #                 }
    #             }
    #         },
    #         404: {"description": "음식을 찾을 수 없습니다."}
    #     },
    # )
    # def get(self, request, id, refrigerator_id):
    #     fridge_food = get_object_or_404(FridgeFood, id=id, refrigerator_id=refrigerator_id)
    #     print(fridge_food)
    #     histories = fridge_food.food_histories.all()
    #     data = [
    #         {
    #             "action": history.action,
    #             "quantity": history.quantity,
    #             "timestamp": history.timestamp,
    #         }
    #         for history in histories
    #     ]
    #     return Response(data, status=200)


class FoodExpirationQueryView(APIView):
    @extend_schema(
        summary="식품 유통기한 조회",
        description="ChatGPT를 사용하여 특정 식품의 평균 유통기한 정보를 반환합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "조회할 식품의 이름",
                        "example": "Milk"
                    }
                },
                "required": ["name"],
            }
        },
        responses={
            200: {
                "type": "object",
                "properties": {
                    "food_name": {
                        "type": "string",
                        "description": "조회된 식품 이름",
                    },
                    "expiration_info": {
                        "type": "string",
                        "description": "ChatGPT로부터 받은 유통기한 정보",
                    },
                },
                "example": {
                    "food_name": "Milk",
                    "expiration_info": "Milk typically lasts 7-10 days in the refrigerator after opening."
                },
            },
            400: {
                "description": "식품 이름이 제공되지 않았을 때",
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

        if not food_name:
            return Response({"error": "Food name is required."}, status=400)

        # ChatGPT API 호출
        try:
            client = OpenAI(api_key=config("OPENAI_API_KEY"))  # 클라이언트 생성
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a food expiration expert."},
                    {"role": "user", "content": f"What is the average expiration date of {food_name}?"}
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