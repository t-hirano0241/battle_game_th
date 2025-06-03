from .status import *
from .base import Skill

__all__ = ['Damage_up', 'Attack_up', 'Defence_up', 'Healing','Burning','Paralysising',
           'DamageHalfing','Confusioning','Regenerationing','Reflectioning','Attack_Drain',
           'CounterStrike']

class Damage_up(Skill):
    def __init__(self,name):
        super().__init__(name,"与えるダメージ量が増える")
    
    def use(self,mymonster,target_monster):
        damage = mymonster._attack * 2
        target_monster.receive_damage(damage)
        return [f"{mymonster.name} のダメージ量が増加し、{target_monster.name} に {damage} ダメージを与えた！"]

class Attack_up(Skill):
    def __init__(self, name):
        super().__init__(name, "攻撃力が増加する")
    
    def use(self,mymonster,target):
        before = mymonster._attack
        attack_up = mymonster._attack * 2
        mymonster._attack = attack_up
        return [
            f"{mymonster.name} の攻撃力が {before} から {attack_up} へ増加した！",
            f"{mymonster.name} の力がみなぎっているようだ..."
        ]

class Defence_up(Skill):
    def __init__(self, name):
        super().__init__(name, "防御力が向上する")
    
    def use(self,mymonster,target):
        before = mymonster._defence
        defence_up = mymonster._defence * 2
        mymonster._defence = defence_up
        return [
            f"{mymonster.name} の防御力が {before} から {defence_up} へ増加した！",
            f"{mymonster.name} はまだまだ耐えられそうだ..."
        ]

class Healing(Skill):
    def __init__(self, name):
        super().__init__(name, "一時的に自身を回復する")
    def use(self,mymonster,target):
        value = mymonster._max_stamina
        mymonster.stamina = value
        return [
            f"{mymonster.name} のスタミナが全回復した！",
            f"{mymonster.name} はまだまだ戦えそうだ..."
        ]

class Burning(Skill):
    def __init__(self, name):
        super().__init__(name, "3ターンの間、相手をやけど状態にする")
    def use(self,mymonster,target):
        damage = mymonster._attack  # 好きな計算式でOK
        dealt=target.receive_damage(damage)
        target.apply_status(Burn(percent=0.25, duration=3))
        return [
            f"{target.name}に{dealt}ダメージを与え,",
            f"{target.name} はやけど状態になった！（3ターン）"]

class Paralysising(Skill):
    def __init__(self, name):
        super().__init__(name, "1ターンの間、相手をまひ状態にする")
    def use(self,mymonster,target):
        damage = mymonster._attack  # 好きな計算式でOK
        dealt=target.receive_damage(damage)
        target.apply_status(Paralysis(duration=1))
        return [
            f"{target.name}に{dealt}ダメージを与え,",
            f"{target.name} はまひ状態になった！（1ターン）"]

class DamageHalfing(Skill):
    def __init__(self, name):
        super().__init__(name, "2ターンの間、相手のダメージを半減する")
    def use(self,mymonster,target):
        mymonster.apply_status(DamageHalf(duration=2))
        return [f"{mymonster.name} のダメージが2ターン半減される！"]

class Confusioning(Skill):
    def __init__(self, name):
        super().__init__(name, "3ターンの間、相手を混乱状態にする")
    def use(self,mymonster,target):
        target.apply_status(Confusion(duration=3, chance=0.3))
        return [f"{target.name} は混乱状態になった！（3ターン、30%で誤動作）"]

class Regenerationing(Skill):
    def __init__(self,name):
        super().__init__(name,"4ターンの間、スタミナがMAXスタミナの20%分回復する")
    def use(self,mymonster,target):
        mymonster.apply_status_regeneration(Regeneration(percent=0.2, duration=4))
        return [f"{mymonster.name} のスタミナが4ターンかけて回復する！（毎ターン20%）"]

class Reflectioning(Skill):
    def __init__(self, name):
        super().__init__(name, "3ターンの間、ダメージを受けた30%のダメージ量を相手に与える")
    def use(self, mymonster, target):
        mymonster.apply_status_myself(Reflection(percent=0.3, duration=3))
        return [f"{mymonster.name} は反射状態になった！（3ターン、30%反射）"]

class Attack_Drain(Skill):
    def __init__(self,name):
        super().__init__(name,"攻撃したダメージ分だけ自身を回復する")
    def use(self, user, target) -> list[str]:
        msgs: list[str] = []

        # 1) ドレイン攻撃のログ
        msgs.append(f"{user.name} のドレイン攻撃！")

        # 2) 実際に与えるダメージ量（防御力差し引き後）を計算
        raw = user._attack
        damage = max(0, raw - target._defence)

        # 3) ダメージ適用
        target.receive_damage(raw, user)
        msgs.append(f"{target.name} に {damage} ダメージ")

        # 4) 回復処理（heal が実際に回復した量を返す）
        healed = user.heal(damage)
        msgs.append(f"{user.name} は {healed} 回復した！")

        return msgs
class CounterStrike(Skill):
    def __init__(self, name):
        super().__init__(name, "次の1回、受けるダメージを無効化し150%反射する（HP20%以下で使用可）")
    def use(self, user, target):
        if user.stamina > user._max_stamina * 0.2:
            return [f"{user.name} のスタミナが高すぎてカウンターストライクを使えない！"]
        user.statuses.append(CounterOffense(duration=1, percent=1.5))
        return [f"{user.name} はカウンターストライク状態になった！（次の1回、150%反射）"]