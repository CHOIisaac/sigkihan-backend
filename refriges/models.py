from django.db import models
from django.db.models import UniqueConstraint


class Refrigerator(models.Model):
    name = models.CharField(max_length=100, verbose_name="냉장고 이름")
    description = models.TextField(null=True, blank=True, verbose_name="냉장고 설명")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 날짜")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 날짜")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'refrigerator'
        verbose_name = '냉장고'


class RefrigeratorAccess(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('member', 'Member'),
    ]
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='refrigerator_access')
    refrigerator = models.ForeignKey(Refrigerator, on_delete=models.CASCADE, related_name='access_list')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="사용자의 역할")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="권한 부여 날짜")

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'refrigerator'], name='unique_user_refrigerator')
        ]
        db_table = 'refrigerator_access'
        verbose_name = '냉장고 공유'

    def __str__(self):
        return f"{self.user.email} - {self.role} of {self.refrigerator.name}"
