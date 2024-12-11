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
    responses={200: DefaultFoodSerializer(many=True)}
)
class DefaultFoodListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DefaultFoodSerializer

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if len(query) >= 1:
            return DefaultFood.objects.filter(name__icontains=query)
        return DefaultFood.objects.all()


class FridgeFoodViewSet(viewsets.ViewSet):
    """
    냉장고 음식 관련 API ViewSet
    """
    permission_classes = [IsAuthenticated]
    # lookup_field = "id"

    @extend_schema(
        summary="내 냉장고 음식 리스트",
        description="사용자의 냉장고에 추가된 모든 음식을 조회합니다.",
        responses={200: FridgeFoodSerializer(many=True)}
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

        serializer = FridgeFoodSerializer(fridge_foods, many=True)
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="음식 추가",
        description="냉장고에 기본 제공 음식 또는 사용자 정의 음식을 추가합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "refrigerator_id": {"type": "integer", "example": 1, "description": "냉장고 ID"},
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
    def create(self, request):
        """
        음식 추가
        """
        refrigerator_id = request.data.get('refrigerator_id')
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
                default_food=default_food,
                purchase_date=purchase_date,
                expiration_date=expiration_date,
                quantity=quantity
            )
        else:
            food = FridgeFood.objects.create(
                refrigerator=refrigerator,
                name=name,
                purchase_date=purchase_date,
                expiration_date=expiration_date,
                quantity=quantity
            )

        serializer = FridgeFoodSerializer(food)
        return Response(serializer.data, status=201)

    @extend_schema(
        summary="냉장고 음식 수정",
        description="냉장고에 있는 음식을 수정합니다. 디폴트 푸드인 경우 구매일자, 소비기한, 수량만 수정 가능하며, 사용자 정의 푸드인 경우 이름도 수정 가능합니다.",
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
        serializer = FridgeFoodSerializer(food)
        return Response(serializer.data, status=200)

    @extend_schema(
        summary="냉장고 음식 삭제",
        description="냉장고에서 특정 음식을 삭제합니다.",
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
    def post(self, request, food_id):
        action = request.data.get('action')
        quantity = request.data.get('quantity')

        if not action or not quantity:
            return Response({"error": "Action and quantity are required."}, status=400)

        fridge_food = get_object_or_404(FridgeFood, id=food_id)

        if action in ['consumed', 'discarded']:
            if fridge_food.quantity < quantity:
                return Response({"error": "Not enough quantity to perform this action."}, status=400)

            fridge_food.quantity -= quantity

            if fridge_food.quantity == 0:
                fridge_food.delete()
            else:
                fridge_food.save()

            FoodHistory.objects.create(
                fridge_food=fridge_food,
                user=request.user,
                action=action,
                quantity=quantity
            )
            return Response({
                "message": f"{action.capitalize()} recorded successfully.",
                "remaining_quantity": fridge_food.quantity
            }, status=201)

        return Response({"error": "Invalid action."}, status=400)

    @extend_schema(
        summary="특정 음식에 대한 히스토리 조회",
        description="냉장고의 특정 음식에 대한 소비 및 폐기 기록을 조회합니다.",
        responses={
            200: {
                "description": "히스토리 조회 성공",
                "content": {
                    "application/json": {
                        "example": [
                            {"action": "consumed", "quantity": 2, "timestamp": "2024-12-11T08:00:00Z"},
                            {"action": "discarded", "quantity": 1, "timestamp": "2024-12-12T09:00:00Z"}
                        ]
                    }
                }
            },
            404: {"description": "음식을 찾을 수 없습니다."}
        },
    )
    def get(self, request, food_id):
        fridge_food = get_object_or_404(FridgeFood, id=food_id)
        histories = fridge_food.food_histories.all()
        data = [
            {
                "action": history.action,
                "quantity": history.quantity,
                "timestamp": history.timestamp,
            }
            for history in histories
        ]
        return Response(data, status=200)
