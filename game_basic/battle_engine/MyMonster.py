from .Monster import MonsterBase
from .skills import *

__all__ = ['Belzebute', 'Rimuru', 'Ikirinko', 'Yukinoryokan', 'Yukinoyado','Peyanggeki',
           'Dengekinokagegiri','Shibirenosuke','Nokusugard','GenmuPrincessBee','Myoibachi',
           'Cellreviver','Kyoumenki','Bloodywizard','Counterblaze']

class Belzebute(MonsterBase):
    EVOLUTION = None
    def __init__(self, level):
        super().__init__("ベルゼビュート", level)
        self.skills.append(Damage_up("グラトニー"))

class Rimuru(MonsterBase):
    EVOLUTION = (Belzebute, 10)
    def __init__(self, level: int = 1):
        super().__init__("リムル", level)
        self.skills.append(Damage_up("グラトニー"))

class Ikirinko(MonsterBase):
    EVOLUTION=None
    def __init__(self,level:int=1):
        super().__init__("イキリンコ", level)
        self.skills.append(Attack_up("喧嘩上等"))


class Yukinoryokan(MonsterBase):
    EVOLUTION=None
    def __init__(self,level):
        super().__init__("雪の旅館",level)
        self.skills.append(Defence_up("守りを固める"))
class Yukinoyado(MonsterBase):
    EVOLUTION=(Yukinoryokan,10)
    def __init__(self, level:int=10):
        super().__init__("雪の宿", level)
        self.skills.append(Defence_up("守りを固める"))

class Peyanggeki(MonsterBase):
    EVOLUTION=None
    def __init__(self,level):
        super().__init__("ペヤング激",level)
        self.skills.append(Burning("激辛コンティニュー"))

class Dengekinokagegiri(MonsterBase):
    EVOLUTION=None
    def __init__(self, level):
        super().__init__("電撃のカゲギリ", level)
        self.skills.append(Paralysising("漆黒雷刃"))

class Shibirenosuke(MonsterBase):
    EVOLUTION=(Dengekinokagegiri,13)
    def __init__(self, level):
        super().__init__("シビレノスケ", level)
        self.skills.append(Paralysising("しびれ手裏剣"))

class Nokusugard(MonsterBase):
    EVOLUTION=None
    def __init__(self, level):
        super().__init__("ノクスガード", level)
        self.skills.append(DamageHalfing("ノクス・ハーフシールド"))

class GenmuPrincessBee(MonsterBase):
    EVOLUTION=None
    def __init__(self, level):
        super().__init__("ゲンムプリンセスビー", level)
        self.skills.append(Confusioning("幻花粉ヴェール"))


class Myoibachi(MonsterBase):
    EVOLUTION=(GenmuPrincessBee,15)
    def __init__(self, level):
        super().__init__("迷い蜂", level)
        self.skills.append(Confusioning("迷いの霧"))

class Cellreviver(MonsterBase):
    EVOLUTION=None
    def __init__(self, level):
        super().__init__("セルリバイバー", level)
        self.skills.append(Regenerationing("オートリジェネレーション"))

class Kyoumenki(MonsterBase):
    EVOLUTION=None
    def __init__(self,  level):
        super().__init__("鏡面鬼", level)
        self.skills.append(Reflectioning("鏡面結界"))

class Bloodywizard(MonsterBase):
    EVOLUTION=None
    def __init__(self, level):
        super().__init__("ブラッディウィザード", level)
        self.skills.append(Attack_Drain("ブラッドリーパー"))

class Counterblaze(MonsterBase):
    EVOLUTION = None

    def __init__(self, level: int = 1):
        # 名前を「カウンターウィザード」、レベルは引数で指定
        super().__init__("カウンターブレイズ", level)
        # カウンターオフェンス・スキルを覚えさせる
        self.skills.append(CounterStrike("リミットブレイク"))