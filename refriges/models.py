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


class RefrigeratorInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    inviter = models.ForeignKey(
        'users.CustomUser', on_delete=models.CASCADE, related_name='sent_invitations', verbose_name="초대한 사람"
    )
    invitee_email = models.EmailField(verbose_name="초대받은 사람 이메일")  # 초대받은 사용자의 이메일
    refrigerator = models.ForeignKey(
        Refrigerator, on_delete=models.CASCADE, related_name='invitations', verbose_name="냉장고"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="초대 상태"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="초대 날짜")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="상태 변경 날짜")

    def __str__(self):
        return f"{self.invitee_email} - {self.refrigerator.name} ({self.status})"

    class Meta:
        db_table = 'refrigerator_invitation'
        verbose_name = '냉장고 초대'
        verbose_name_plural = '냉장고 초대'
        ordering = ['-created_at']