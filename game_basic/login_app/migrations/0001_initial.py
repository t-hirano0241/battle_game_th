# Generated by Django 5.2.1 on 2025-05-10 08:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('base_hp', models.PositiveIntegerField(default=20)),
                ('base_attack', models.PositiveIntegerField(default=10)),
                ('base_defense', models.PositiveIntegerField(default=5)),
                ('level', models.PositiveSmallIntegerField(default=1, editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveSmallIntegerField(default=1, verbose_name='レベル')),
                ('win_count', models.PositiveIntegerField(default=0, verbose_name='勝利数')),
                ('loss_count', models.PositiveIntegerField(default=0, verbose_name='敗北数')),
                ('favorite_mon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='favored_by', to='login_app.monster', verbose_name='お気に入りモンスター')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
        ),
        migrations.CreateModel(
            name='Rank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_level', models.PositiveSmallIntegerField(help_text='この称号が適用される最小レベル')),
                ('max_level', models.PositiveSmallIntegerField(help_text='この称号が適用される最大レベル')),
                ('title', models.CharField(help_text='称号名', max_length=30)),
                ('description', models.TextField(help_text='称号の説明文')),
            ],
            options={
                'ordering': ['min_level'],
                'unique_together': {('min_level', 'max_level')},
            },
        ),
        migrations.AddField(
            model_name='monster',
            name='skill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='monsters', to='login_app.skill'),
        ),
        migrations.CreateModel(
            name='MonsterSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login_app.monster')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='login_app.skill')),
            ],
            options={
                'unique_together': {('monster', 'skill')},
            },
        ),
    ]
