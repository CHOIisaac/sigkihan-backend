# Generated by Django 5.0.3 on 2025-01-14 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refriges', '0004_alter_refrigeratorinvitation_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refrigeratorinvitation',
            name='code',
            field=models.CharField(default='uVZuIcI1W0gnhs7YPgF7BQ', max_length=50, unique=True, verbose_name='초대 코드'),
        ),
    ]
