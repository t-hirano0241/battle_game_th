import random

__all__=['Burn','Paralysis','DamageHalf','Confusion','Regeneration',
         'Reflection','CounterOffense']

class Status:
    """
    継続ターン管理とログ返却の基底クラス
    """
    name: str
    duration: int

    def __init__(self, duration: int):
        self.duration = duration

    def tick(self):
        self.duration -= 1

    # デフォルトで何もしない前受けフック
    def on_before_receive(self, monster, incoming: int) -> int:
        return incoming

    # デフォルトで何もしない後受けフック
    def on_after_receive(self, monster, attacker, blocked: int = 0):
        pass

    def on_turn_end(self, monster, target=None) -> list[str]:
        msgs: list[str] = []
        self.tick()
        if self.duration <= 0:
            msgs.append(f"{monster.name} の {self.name} が解除された！")
        return msgs

class Burn(Status):
    name = "やけど"
    def __init__(self, percent: float = 0.25, duration: int = 3):
        super().__init__(duration)
        self.percent = percent

    def on_turn_end(self, monster, target=None) -> list[str]:
        msgs: list[str] = []
        dmg = int(monster._max_stamina * self.percent)
        monster.status_damage(dmg)
        msgs.append(f"{monster.name} は {self.name} で {dmg} ダメージ")
        msgs += super().on_turn_end(monster, target)
        return msgs

class Paralysis(Status):
    name = "まひ"
    def __init__(self, duration: int = 1):
        super().__init__(duration)

    def on_turn_end(self, monster, target=None) -> list[str]:
        return super().on_turn_end(monster, target)

class DamageHalf(Status):
    name = "ダメージ半減"
    def __init__(self, duration: int = 2):
        super().__init__(duration)

    def on_before_receive(self, monster, incoming: int) -> int:
        return incoming // 2

    def on_turn_end(self, monster, target=None) -> list[str]:
        return super().on_turn_end(monster, target)

class Confusion(Status):
    name = "混乱"
    def __init__(self, duration: int = 3, chance: float = 0.3):
        super().__init__(duration)
        self.chance = chance

    def on_before_action(self, monster, target) -> bool:
        return random.random() <= self.chance

    def on_turn_end(self, monster, target=None) -> list[str]:
        return super().on_turn_end(monster, target)

class Regeneration(Status):
    name = "リジェネレーション"
    def __init__(self, percent: float = 0.2, duration: int = 4):
        super().__init__(duration)
        self.percent = percent

    def on_turn_end(self, monster, target=None) -> list[str]:
        msgs: list[str] = []
        heal_val = int(monster._max_stamina * self.percent)
        monster.stamina += heal_val
        msgs.append(f"{monster.name} は {heal_val} 回復 (リジェネ)")
        msgs += super().on_turn_end(monster, target)
        return msgs

class Reflection(Status):
    name = "リフレクション"
    def __init__(self, percent: float = 0.3, duration: int = 3):
        super().__init__(duration)
        self.percent = percent
        self.attacker = None

    def on_before_receive(self, monster, incoming: int) -> int:
        return incoming

    def on_after_receive(self, monster, attacker, blocked: int = 0):
        self.attacker = attacker

    def on_turn_end(self, monster, target=None) -> list[str]:
        msgs: list[str] = []
        if self.attacker:
            dmg = int(monster.last_damage_taken * self.percent)
            msgs.append(f"{monster.name} は {self.name} で {dmg} 反射")
            msgs.extend(target.status_damage(dmg))
        msgs += super().on_turn_end(monster, target)
        return msgs

class CounterOffense(Status):
    name = "カウンターオフェンス"
    def __init__(self, percent: float = 1.5, duration: int = 1):
        super().__init__(duration)
        self.percent = percent
        self.blocked = 0
        self.attacker = None

    def on_before_receive(self, monster, incoming: int) -> int:
        self.blocked = incoming
        return 0

    def on_after_receive(self, monster, attacker, blocked: int):
        self.attacker = attacker

    def on_turn_end(self, monster, target=None) -> list[str]:
        msgs: list[str] = []
        if self.attacker and self.blocked > 0:
            reflect = int(self.blocked * self.percent)
            msgs.append(f"{monster.name} は {self.name} で {reflect} 反撃")
            self.attacker.receive_damage(reflect, monster)
        msgs += super().on_turn_end(monster, target)
        return msgs

class SpecialCooldown(Status):
    """
    必殺技（スペシャルアタック）使用後のクールダウン管理用ステータス。
    duration ターンの間、再度スペシャル技が使用できなくなります。
    """
    name = "SpecialCooldown"

    def __init__(self, duration: int = 2):
        # デフォルト 2 ターンのクールダウン（お好みで変更可）
        super().__init__(duration=duration)