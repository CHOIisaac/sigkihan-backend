from django.db import models


# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='notification', verbose_name='사용자')
    fridge_food = models.ForeignKey('foods.FridgeFood', on_delete=models.CASCADE, related_name='notifications',verbose_name='냉장고 식품')
    message = models.TextField(verbose_name='알림 메시지')
    is_read = models.BooleanField(default=False, verbose_name='읽음 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')

    class Meta:
        db_table = 'notification'
        verbose_name = '알림'
        verbose_name_plural = '알림'

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message}"
