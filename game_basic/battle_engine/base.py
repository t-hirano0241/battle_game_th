
# base.py
from abc import ABC, abstractmethod

# 抽象モンスターインターフェース
class Monster(ABC):
    @abstractmethod
    def receive_damage(self, amount: int) -> None:
        pass

    @abstractmethod
    def end_of_turn(self) -> None:
        pass

    @abstractmethod
    def attack(self, target: 'Monster') -> None:
        pass

    @abstractmethod
    def heal(self, amount: int) -> None:
        pass

# 抽象スキルインターフェース
class Skill(ABC):
    def __init__(self,name,description):
        self.name=name
        self.skill_name = name
        self._description=description

    @abstractmethod
    def use(self, user: Monster, target: Monster) -> None:
        pass

# 抽象状態異常インターフェース
class Status(ABC):
    name: str

    def __init__(self, duration: int):
        self.duration = duration

    @abstractmethod
    def on_turn_end(self, monster: Monster) -> None:
        pass

    @abstractmethod
    def on_after_attacked(self, monster: Monster, attacker: Monster) -> None:
        pass

    def on_before_receive(self, monster, incoming: int) -> int:
        return incoming

    def on_after_receive(self, monster, attacker, blocked: int) -> None:
        pass

    def tick(self, monster: Monster) -> None:
        self.duration -= 1
        if self.duration <= 0:
            monster.statuses.remove(self)
            print(f"{monster.name} の {self.name} が解除された！")
