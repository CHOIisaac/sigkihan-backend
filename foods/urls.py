from rest_framework.routers import DefaultRouter
from django.urls import path

from foods.views import DefaultFoodListView, FridgeFoodViewSet, FoodHistoryView


class NoSlashRouter(DefaultRouter):
    """
    URL 끝에 슬래시를 제거하는 라우터
    """
    def __init__(self):
        super().__init__()
        self.trailing_slash = ''  # 슬래시 제거


router = NoSlashRouter()
router.register(r'refrigerators/<int:refrigerator_id>/foods', FridgeFoodViewSet, basename='fridge-food')


urlpatterns = [
    path('default-foods', DefaultFoodListView.as_view(), name='default-food-list'),
    path('refrigerators/<int:refrigerator_id>/foods', FridgeFoodViewSet.as_view({'get': 'list', 'post': 'create'}), name='fridge-food-list'),
    path('refrigerators/<int:refrigerator_id>/foods/<int:id>', FridgeFoodViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='fridge-food-detail'),
    # path('foods/fridge/<int:food_id>/history', FoodHistoryView.as_view(), name='food-history'),
] + router.urls