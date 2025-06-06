# Generated by Django 5.2.1 on 2025-05-22 01:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0014_rename_defense_per_level_monster_defence_per_level'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeAttackRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('elapsed_time', models.DurationField(verbose_name='クリアに要した時間')),
                ('cleared_at', models.DateTimeField(auto_now_add=True, verbose_name='達成日時')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name': 'タイムアタック記録',
                'verbose_name_plural': 'タイムアタック記録',
                'ordering': ['elapsed_time'],
            },
        ),
    ]
