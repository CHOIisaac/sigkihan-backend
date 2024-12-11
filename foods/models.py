from django.db import models


# Create your models here.
class DefaultFood(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='기본 식품 이름')
    image = models.ImageField(upload_to='food_images/', verbose_name='기본 식품 이미지')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'default_food'
        verbose_name = '기본 식품'


class FridgeFood(models.Model):
    refrigerator = models.ForeignKey(
        'refriges.Refrigerator', on_delete=models.CASCADE, related_name='refrigerator_foods', verbose_name='냉장고'
    )
    default_food = models.ForeignKey(
        'DefaultFood', on_delete=models.CASCADE, null=True, blank=True, related_name='default_foods', verbose_name='기본 식품'
    )
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name="사용자 정의 식품 이름")
    purchase_date = models.DateField(verbose_name='구매 날짜')
    expiration_date = models.DateField(verbose_name='소비기한')
    quantity = models.PositiveIntegerField(default=1, verbose_name='수량')

    def __str__(self):
        food_name = self.default_food.name if self.default_food else self.name
        return f"{food_name} - {self.refrigerator.name}"

    class Meta:
        db_table = 'fridge_food'
        verbose_name = '냉장고 식품'
        verbose_name_plural = '냉장고 식품'


class FoodHistory(models.Model):
    ACTION_CHOICES = [
        ('consumed', 'Consumed'),  # 먹었어요
        ('discarded', 'Discarded'),  # 폐기했어요
    ]

    fridge_food = models.ForeignKey(
        FridgeFood, on_delete=models.CASCADE, related_name='food_histories', verbose_name='냉장고 식품'
    )
    user = models.ForeignKey(
        'users.CustomUser', on_delete=models.CASCADE, related_name='food_histories', verbose_name='사용자'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name='행동 유형')
    quantity = models.PositiveIntegerField(verbose_name='수량', help_text='소비하거나 폐기한 수량')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='기록 시간')

    def __str__(self):
        return f"{self.user.name} - {self.get_action_display()} {self.quantity} ({self.timestamp})"

    class Meta:
        db_table = 'food_history'
        verbose_name = '식품 기록'
        verbose_name_plural = '식품 기록'


# class CustomFood(models.Model):
#     name = models.CharField(max_length=100, unique=True, verbose_name='사용자 정의 식품 이름')
#     image = models.ImageField(default='default_food_images/custom_food.jpg', verbose_name='사용자 정의 식품 이미지')
#     description = models.TextField(blank=True, null=True, verbose_name='식품 설명')
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         db_table = 'custom_food'
#         verbose_name = '사용자 정의 식품'