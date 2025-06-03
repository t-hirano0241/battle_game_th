from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Skill(models.Model):
    name        = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Monster(models.Model):
    name               = models.CharField(max_length=50, unique=True)
    level              = models.PositiveIntegerField(default=1)
    description        = models.TextField(blank=True)
    base_hp            = models.PositiveIntegerField(default=20)
    hp_per_level       = models.PositiveIntegerField(default=10)
    base_attack        = models.PositiveIntegerField(default=10)
    attack_per_level   = models.PositiveIntegerField(default=8)
    base_defence       = models.PositiveIntegerField(default=5)
    defence_per_level  = models.PositiveIntegerField(default=4)
    skill              = models.ForeignKey(
        Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name='monsters'
    )
    image_front        = models.ImageField(upload_to='monsters/front/', blank=True, null=True)
    image_back         = models.ImageField(upload_to='monsters/back/',  blank=True, null=True)
    
    def current_hp(self):
        return self.base_hp + self.hp_per_level * (self.level - 1)

    def current_attack(self):
        return self.base_attack + self.attack_per_level * (self.level - 1)

    def current_defence(self):
        return self.base_defense + self.defense_per_level * (self.level - 1)

    def __str__(self):
        return self.name


class UserMonster(models.Model):
    user       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='monsters'
    )
    template   = models.ForeignKey(
        'login_app.Monster', on_delete=models.PROTECT
    )
    level      = models.PositiveSmallIntegerField(default=1)
    experience = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user', 'template'),)
        ordering        = ['template__name']

    def __str__(self):
        return f"{self.user.username} の {self.template.name} (Lv{self.level})"

    def experience_to_next_level(self) -> int:
        """
        次のレベルまでに必要な経験値を返す。
        ここでは「現在のレベルの 2 乗 × 100」としています。
        """
        return self.level * self.level * 100

    def gain_experience(self, xp: int) -> tuple[int, int]:
        """
        xp 分の経験値を加算し、必要であればレベルアップを繰り返す。
        レベル上限は 20 とし、以降の経験値はリセット。
        最終的な (old_level, new_level) を返します。
        """
        old_level = self.level
        self.experience += xp

        # レベルアップループ
        while self.experience >= self.experience_to_next_level() and self.level < 20:
            self.experience -= self.experience_to_next_level()
            self.level += 1

        # 上限到達時は経験値をクリア
        if self.level >= 20:
            self.level = 20
            self.experience = 0

        # 変更のあったフィールドだけ保存
        self.save(update_fields=['experience', 'level', 'updated_at'])
        return old_level, self.level

class MonsterSkill(models.Model):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    skill   = models.ForeignKey(Skill,   on_delete=models.CASCADE)

    class Meta:
        unique_together = (('monster', 'skill'),)

    def __str__(self):
        return f"{self.monster.name} → {self.skill.name}"


class TimeAttackRecord(models.Model):
    user          = models.OneToOneField(
                        User,
                        on_delete=models.CASCADE,
                        verbose_name="ユーザー"
                    )
    elapsed_time  = models.DurationField(verbose_name="クリアに要した時間")
    cleared_at    = models.DateTimeField(auto_now_add=True, verbose_name="達成日時")

    class Meta:
        ordering = ['elapsed_time']
        verbose_name = "タイムアタック記録"
        verbose_name_plural = "タイムアタック記録"


# class Rank(models.Model):
#     min_level   = models.PositiveSmallIntegerField(help_text="この称号が適用される最小レベル")
#     max_level   = models.PositiveSmallIntegerField(help_text="この称号が適用される最大レベル")
#     title       = models.CharField(max_length=30, help_text="称号名")
#     description = models.TextField(help_text="称号の説明文")

#     class Meta:
#         ordering = ['min_level']
#         unique_together = (('min_level', 'max_level'),)

#     def __str__(self):
#         return f"Lv{self.min_level}〜{self.max_level}: {self.title}"

class Profile(models.Model):
    user           = models.OneToOneField(
                       User,
                       on_delete=models.CASCADE,
                       verbose_name="ユーザー"
                     )
    # ───────────────────────────────────────────────────
    # ここで「ベスト記録」を TimeAttackRecord に紐づける
    best_record    = models.OneToOneField(
                       TimeAttackRecord,
                       on_delete=models.SET_NULL,
                       null=True,
                       blank=True,
                       verbose_name="ベストタイム記録",
                       related_name='+'
                     )
    # ───────────────────────────────────────────────────
    favorite_mon   = models.ForeignKey(
                       Monster,
                       on_delete=models.SET_NULL,
                       null=True,
                       blank=True,
                       verbose_name="お気に入りモンスター",
                       related_name='favored_by'
                     )

    def __str__(self):
        return f"{self.user.username}のプロフィール"