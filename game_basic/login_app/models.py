from django.db import models
from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    name        = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Monster(models.Model):
    name         = models.CharField(max_length=50)
    description  = models.TextField(blank=True)
    base_hp=models.PositiveIntegerField(default=20)
    base_attack  = models.PositiveIntegerField(default=10)
    base_defense = models.PositiveIntegerField(default=5)
    skill        = models.ForeignKey(
                       Skill,
                       on_delete=models.SET_NULL,
                       null=True,
                       blank=True,
                       related_name='monsters'
                   )
    level        = models.PositiveSmallIntegerField(default=1, editable=False)

    def __str__(self):
        return self.name

class MonsterSkill(models.Model):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    skill   = models.ForeignKey(Skill,   on_delete=models.CASCADE)

    class Meta:
        unique_together = (('monster', 'skill'),)

    def __str__(self):
        return f"{self.monster.name} → {self.skill.name}"

class Rank(models.Model):
    min_level   = models.PositiveSmallIntegerField(help_text="この称号が適用される最小レベル")
    max_level   = models.PositiveSmallIntegerField(help_text="この称号が適用される最大レベル")
    title       = models.CharField(max_length=30, help_text="称号名")
    description = models.TextField(help_text="称号の説明文")

    class Meta:
        ordering = ['min_level']
        unique_together = (('min_level', 'max_level'),)

    def __str__(self):
        return f"Lv{self.min_level}〜{self.max_level}: {self.title}"

class Profile(models.Model):
    user         = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="ユーザー")
    level        = models.PositiveSmallIntegerField(default=1, verbose_name="レベル")
    win_count    = models.PositiveIntegerField(default=0, verbose_name="勝利数")
    loss_count   = models.PositiveIntegerField(default=0, verbose_name="敗北数")
    favorite_mon = models.ForeignKey(
                       Monster,
                       on_delete=models.SET_NULL,
                       null=True,
                       blank=True,
                       verbose_name="お気に入りモンスター",
                       related_name='favored_by'
                   )
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"{self.user.username} (Lv{self.level})"