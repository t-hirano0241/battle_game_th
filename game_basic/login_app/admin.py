# login_app/admin.py
from django.contrib import admin
from .models import Monster, Skill, Rank, MonsterSkill

# ① 中間テーブル用の Inline クラスを定義
class MonsterSkillInline(admin.TabularInline):
    model = MonsterSkill
    extra = 1

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display  = ('name',)
    search_fields = ('name',)

@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display  = ('min_level', 'max_level', 'title')
    search_fields = ('title',)
    list_filter   = ('min_level', 'max_level')

@admin.register(Monster)
class MonsterAdmin(admin.ModelAdmin):
    # ② 一覧に出したいフィールドを定義
    list_display        = (
        'name',
        'skill',
        'base_hp',
        'base_attack',
        'base_defense',
        'level',
        'short_desc',
    )
    list_select_related = ('skill',)
    search_fields       = ('name', 'skill__name')
    list_filter         = ('skill', 'level')

    # ③ ここで Inline を登録して「MonsterSkill」を一画面で管理
    inlines = [MonsterSkillInline]

    @admin.display(description='説明')
    def short_desc(self, obj):
        text = obj.description or ''
        return text if len(text) <= 40 else text[:40] + '…'
