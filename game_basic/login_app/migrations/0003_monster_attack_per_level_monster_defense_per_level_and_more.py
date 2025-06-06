# Generated by Django 5.2.1 on 2025-05-12 14:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0002_profile_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='attack_per_level',
            field=models.PositiveIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='monster',
            name='defense_per_level',
            field=models.PositiveIntegerField(default=4),
        ),
        migrations.AddField(
            model_name='monster',
            name='hp_per_level',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='monster',
            name='level',
            field=models.PositiveIntegerField(default=20),
        ),
        migrations.AlterField(
            model_name='monster',
            name='skill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='monsters', to='login_app.skill', verbose_name='特殊技'),
        ),
    ]
