# Generated by Django 5.0.3 on 2024-12-14 07:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('refriges', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='알림 메시지')),
                ('d_day', models.CharField(max_length=10, verbose_name='디데이 정보')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성 날짜')),
                ('is_read', models.BooleanField(default=False, verbose_name='읽음 여부')),
                ('refrigerator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='refriges.refrigerator', verbose_name='냉장고')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '알림',
                'verbose_name_plural': '알림',
                'db_table': 'notification',
                'ordering': ['-created_at'],
            },
        ),
    ]
