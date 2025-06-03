from .base import Monster
from .skills import Skill
from .status import Status
from .status import *
from .status import SpecialCooldown
import random

class MonsterBase(Monster):
    BASE_HP        = 25    # Lv1 のときの HP
    HP_PER_LEVEL   = 10   
    BASE_ATK       = 20    # Lv1 のときの攻撃力
    ATK_PER_LEVEL  = 8     # レベルあたり攻撃力の増分
    BASE_DEF       = 10     # Lv1 のときの守備力
    DEF_PER_LEVEL  = 4     # レベルあたり守備力の増分

    EVOLUTION:tuple[type['Monster'],int]|None=None

    def __init__(self, name, level):
        self.name=str(name)
        self._level=int(level)
        self._recalc_stats()
        self._stamina     = self._max_stamina
        self.is_dead=False
        self._exp=0
        self._exp_to_next=self._calc_exp_need()
        self.skills:list[Skill]=[]
        self.statuses: list[Status] = []
        self.last_damage_taken: int = 0
        self.front_url=''
        self.back_url=''

    def to_dict(self):
        return {
            'name':      self.name,
            'level':     self._level,
            'hp':        max(self.stamina,0),
            'max_hp':    self._max_stamina,
            'attack':self._attack,
            'defence':self._defence,
            'front_url': self.front_url,
            'back_url':  self.back_url,
        }
    def decide_action(self, target) -> str:
        """
        敵 AI 用：今使う行動を文字列で返す
        'attack'         = 通常攻撃
        'special-attack' = 必殺技
        """
        # スキル未習得なら通常攻撃一択
        if not self.skills:
            return 'attack'
        # HP が半分以下で 50% の確率で必殺技
        if self.stamina <= self._max_stamina * 0.5 and random.random() < 0.5:
            return 'special-attack'
        # 普通は 20% の確率で必殺技
        if random.random() < 0.2:
            return 'special-attack'
        return 'attack'



    @property
    def stamina(self):
        return self._stamina
    
    @stamina.setter
    def stamina(self,value):
        value=int(value)
        if value<0:
            value=0
        elif value>self._max_stamina:
            value=self._max_stamina
        self._stamina=value

        if self._stamina==0 and not self.is_dead:
            print(f"{self.name}が倒された")
            self.is_dead=True
        #self.is_dead が True → not self.is_dead は False
        #self.is_dead が False → not self.is_dead は True
        #戦闘不能になった瞬間に一度だけメッセージを表示でき、以降は繰り返し表示することを防げます。
        #同じモンスターに2回攻撃したときに、メッセージの繰り返しをなくす。

    @property
    def exp(self):
        return self._exp
    
    @property
    def level(self):
        return self._level

    def attack(self,target):
        damage=self._attack
        msgs=[f"{self.name}の攻撃!"]
        dealt=target.receive_damage(damage,self)
        msgs.append(f"{target.name}に{dealt}ダメージ")
        return msgs
    
    
    # monster.py
    def receive_damage(self, raw_damage, attacker=None):
    # 1) フック before
        for st in self.statuses:
            raw_damage = st.on_before_receive(self, raw_damage)
    # 2) 通常ダメージ処理
        damage = max(0, raw_damage - self._defence)
        self.last_damage_taken = damage
        self.stamina -= damage
    # 3) フック after
        blocked = raw_damage - damage
        for st in self.statuses:
            st.on_after_receive(self, attacker, blocked)
        return damage

    def heal(self, value: int) -> int:
        """
        スタミナを value だけ回復し、
        実際に回復した量（上限クリップ後の差分）を返す。
        """
        # 負の値は無視
        amount = max(0, int(value))

        # 回復前スタミナを覚えておく
        old_hp = self.stamina

        # スタミナに加算（プロパティで自動クリップされる）
        self.stamina += amount

        # 実際に増えた分を計算
        healed = self.stamina - old_hp

        return healed

    
    def _calc_exp_need(self):
        return (self._level*2)*5
    
    def _recalc_stats(self):
        # レベルに合わせて能力値を再計算
        self._max_stamina = self.BASE_HP    + self.HP_PER_LEVEL  * (self._level - 1)
        self._attack      = self.BASE_ATK   + self.ATK_PER_LEVEL * (self._level - 1)
        self._defence     = self.BASE_DEF   + self.DEF_PER_LEVEL * (self._level - 1)
        # __init__ 時にはここで全回復している想定なので…
        
    #レベルアップ処理
    def level_up(self,value):
        value=int(value)

        if value<0:
            value=0
        
        self._exp=self._exp+value

        while self._exp>=self._exp_to_next:
            self._level+=1
            print(f"{self.name}のレベルが上がった!")
            print(f"{self.name}のレベルは{self.level}になった！")
            self._recalc_stats()
            self._stamina     = self._max_stamina
            self._exp_to_next=self._calc_exp_need()
        rest=self._exp_to_next-self._exp
        print(f"次のレベルアップまで、残り:{rest}")
        return self.try_evolve()
            
    def try_evolve(self):
        """進化できるなら進化後のインスタンスを返し、できなければ自分を返す"""
        if self.EVOLUTION is None:
            return self  # 進化なし
        next_cls, req_level = self.EVOLUTION
        if self.level >= req_level:
            # 進化先を生成（レベルはそのまま引き継ぐ）
            evolved = next_cls(self.level)
            print(f"{self.name}→{evolved.name} に進化！")
            return evolved
        return self
            
        
        #相手レベルに応じた経験量計算
    def get_exp(self,target):
            #レベルが大きいほど、もらえる経験値が多く。
            #レベルが小さいほど、もらえる経験値が少ない。
            #１レベルのやつだと、10だが、10レベルだと100もらえるみたいな
            #20れべのときは、1れべのやつから、30もらえるところが、100れべやと、5しかもらえない
        value=(target._level/self._level)
        
        if 0<value<1:
            value=value*35
        else:
            value=value*20
        value=int(value)
        print(f"{self.name}は,{value}の経験値を得た!")
        self.level_up(value)

            

#状態異常関連

    def apply_status(self, status: Status):
        print(f"{self.name} は {status.name} となった….")
        self.statuses.append(status)
        # ← ここにインデントを合わせる
        print(f"▶ 現在の statuses: {[type(st).__name__ for st in self.statuses]}")

    def apply_status_myself(self, status: Status):
        print(f"{self.name} は {status.name} を発動した!")
        self.statuses.append(status)
        # ← 必要ならこちらにも
        print(f"▶ 現在の statuses: {[type(st).__name__ for st in self.statuses]}")

    def apply_status_regeneration(self, status: Status):
        """リジェネ用のフック。通常の apply_status と同じで OK なら一行にまとめても可."""
        self.apply_status(status)

    def end_of_turn(self, target) -> list[str]:
        msgs: list[str] = []
        for st in list(self.statuses):
            ev = st.on_turn_end(self, target)
            msgs.extend(ev)
            if st.duration <= 0:
                self.statuses.remove(st)
        return msgs

    def status_damage(self,damage):
        msgs: list[str] = []
        self.stamina-=damage
        msgs.append(f"{self.name}は反射により、{damage}ダメージを受けた...")
        return msgs

    def take_turn(self,  target) -> list[str]:
        msgs: list[str] = []
        action=self.decide_action(target)

        # 麻痺チェック
        if any(isinstance(st, Paralysis) for st in self.statuses):
            msgs.append(f"{self.name} は麻痺で行動できない…")
            return msgs

        # 混乱チェック
        for st in self.statuses:
            if isinstance(st, Confusion):
                if st.on_before_action(self, target):
                    msgs.append(f"{self.name} は混乱を振り切って攻撃！")
                    dmg_msgs = self.attack(target) or[]
                    return msgs + dmg_msgs
                else:
                    msgs.append(f"{self.name} は混乱して自分を攻撃してしまった…")
                    dmg_msgs = self.attack(self) or[]
                    return msgs + dmg_msgs
        msgs.append(f"敵：{self.name}の攻撃")
        # 通常行動 or 必殺技
        if action == 'attack':
            dmg_msgs = self.attack(target) or[]
        elif action == 'special-attack':
            msgs.append(f"{self.name} の必殺技！")
            # skill.use() はログ list[str] を返す想定
            dmg_msgs = (self.skills[0].use(self, target)or [])
        else:
            return [f"{self.name} は何もしなかった…"]

        return msgs + (dmg_msgs or [])
    
    def take_my_turn(self, action: str, target) -> list[str]:
        msgs: list[str] = []

    # 麻痺チェック
        if any(isinstance(st, Paralysis) for st in self.statuses):
         return [f"{self.name} は麻痺で行動できない…"]

    # 混乱チェック
        for st in self.statuses:
            if isinstance(st, Confusion):
                if st.on_before_action(self, target):
                    msgs.append(f"{self.name} は混乱を振り切って攻撃！")
                    msgs.extend(self.attack(target))
                else:
                    msgs.append(f"{self.name} は混乱して自分を攻撃してしまった…")
                    msgs.extend(self.attack(self))
                return msgs

    # 通常 or 必殺技
        if action == 'attack':
            msgs.append(f"{self.name} の通常攻撃！")
            msgs.extend(self.attack(target))

        elif action == 'special-attack':
            skill = self.skills[0]
            msgs.append(f"{self.name} の必殺技：{skill.name}！")
            msgs.extend(skill.use(self, target) or [])
            self.apply_status(SpecialCooldown(duration=2))
        else:
             msgs.append(f"{self.name} は何もしなかった…")

        return msgs