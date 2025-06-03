import random
from login_app.models import Monster
from battle_engine.Monster import MonsterBase
from battle_engine.MyMonster import (
    Belzebute, Rimuru, Ikirinko, Yukinoryokan, Yukinoyado,
    Peyanggeki, Dengekinokagegiri, Shibirenosuke, Nokusugard,
    GenmuPrincessBee, Myoibachi, Cellreviver, Kyoumenki,
    Bloodywizard, Counterblaze
)

# テンプレート名→Pythonクラス対応表
CLASS_MAP = {
    "ベルゼビュート":        Belzebute,
    "リムル":                Rimuru,
    "イキリンコ":            Ikirinko,
    "雪の旅館":              Yukinoryokan,
    "雪の宿":                Yukinoyado,
    "ペヤング激":            Peyanggeki,
    "電撃のカゲギリ":        Dengekinokagegiri,
    "シビレノスケ":          Shibirenosuke,
    "ノクスガード":          Nokusugard,
    "ゲンムプリンセスビー":  GenmuPrincessBee,
    "迷い蜂":                Myoibachi,
    "セルリバイバー":        Cellreviver,
    "鏡面鬼":                Kyoumenki,
    "ブラッディウィザード":  Bloodywizard,
    "カウンターブレイズ":    Counterblaze,
}

def calc_xp_gain(enemy_level: int) -> int:
    return enemy_level * enemy_level * 10

def sample_enemy_model() -> Monster:
    return Monster.objects.order_by('?').first()

def build_python_mon_from_model(model: Monster, level: int=None) -> MonsterBase:
    # クラス選択＆レベル補正
    cls = CLASS_MAP.get(model.name, MonsterBase)
    lvl = min(level or model.level, 20)
    mon = cls(lvl)
    # 画像 URL をセット
    mon.front_url = model.image_front.url if model.image_front else ''
    mon.back_url  = model.image_back.url  if model.image_back  else ''
    # ステータス上書き
    mon.BASE_HP, mon.HP_PER_LEVEL = model.base_hp, model.hp_per_level
    mon.BASE_ATK, mon.ATK_PER_LEVEL = model.base_attack, model.attack_per_level
    mon.BASE_DEF, mon.DEF_PER_LEVEL = model.base_defence, model.defence_per_level
    mon._recalc_stats(); mon.stamina = mon._max_stamina
    return mon

def build_enemy_instance(level: int=5) -> MonsterBase:
    mdl = sample_enemy_model()
    return build_python_mon_from_model(mdl, level)