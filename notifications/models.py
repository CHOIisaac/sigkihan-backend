from django.db import models


# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='notifications', verbose_name='사용자')
    refrigerator = models.ForeignKey('refriges.Refrigerator', on_delete=models.CASCADE, verbose_name='냉장고')
    message = models.TextField(verbose_name='알림 메시지')
    d_day = models.CharField(max_length=10, verbose_name="디데이 정보")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 날짜')
    is_read = models.BooleanField(default=False, verbose_name='읽음 여부')

    class Meta:
        db_table = 'notification'
        verbose_name = '알림'
        verbose_name_plural = '알림'
        ordering = ['-created_at']  # 최신순 정렬

    def __str__(self):
        return f"{self.user.name} - {self.message}"
