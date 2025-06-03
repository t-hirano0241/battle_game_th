from Monster import Monster
from EnemyMonster import EnemyMonster
from after_finish import after_finish
from after_finish import cannot_fight
from player import Player
from item import Get_item
from item import Heal_item
from item import Drop_item
from MyMonster import *

import random
import time

user=Player("タクト",0)
user.add_money(5000)

heal_potion       = Heal_item("キズぐすり", 300, 20)
pokeball     = Get_item("モンスターボール", price=200, rate=1.0)
superball    = Get_item("スーパーボール",   price=500, rate=1.5)
hyperball    = Get_item("ハイパーボール",   price=1000,rate=2.0)
attack_potion=Drop_item("パワーアップポーション")
defence_potion=Drop_item("ガードアップポーション")

all_items:dict[str, Heal_item | Get_item | Drop_item] = {
    heal_potion.name:heal_potion,
    pokeball.name:pokeball,
    superball.name:superball,
    hyperball.name:hyperball,
    attack_potion.name:attack_potion,
    defence_potion.name:defence_potion
}

user.add_item(pokeball)
user.add_item(pokeball)
user.add_item(pokeball)
user.add_item(heal_potion)

user.item_box


enemy_templates = [
 {"name":"ゴブリン","level":8},
 {"name":"スケルトン","level":8},
 {"name":"オーク","level":8},
 {"name":"ゴーレム","level":8}
]


monster_list = [
    Rimuru(9),
    Ikirinko(10),
    Yukinoyado(8),
    Peyanggeki(9),
    Shibirenosuke(9),
    Nokusugard(9),
    Myoibachi(9),
    Cellreviver(9),
    Kyoumenki(9),
    Bloodywizard(10),
    Counterblaze(9)


    
]

# 2. 辞書に変換して player にセット
user._mymonster_box = {
    m.name: m
    for m in monster_list
}


def randaom_Enemy():
    tp1=random.choice(enemy_templates)
    return EnemyMonster(tp1["name"],tp1["level"])


#ゲームスタートあるいはstartとユーザが入力したら、ゲームが始まるようにしたい
#進化を実装すると仮定した場合、1進化と2進化用で分けておく。

def switch_monster(mymonster_box,mymonster):
    mons=list(mymonster_box.values())
    n=len(mons)
    
    while True:
        for i,m in enumerate(mons,start=1):
            print(f"{i}: {m.name} ,レベル:{m.level}, スタミナ:{m.stamina}")
        try:
            print("\n")
            print("交代させるモンスターを選択しよう")
            m_choice=input(f"この中から、選んでね(1~{n}の番号を入力してね ※Enterを押すと、戻るよ)")
            if not m_choice:
                return mymonster
                
                

            m_choice=int(m_choice)
            
            if not 1<=m_choice<=n:
                raise ValueError
                
        
        except ValueError:
            print(f"1~{n}の数字を入力してね")
        
        selected=mons[m_choice-1]
        if selected.stamina==0:
            print("\n")
            print("このモンスターは交代できません")
            print("\n")
            continue
        if selected.name==mymonster.name:
            print(f"{selected.name}、もう少し頑張ってくれ！")
            return selected
        print(f"{selected.name}に交代だ!")
        return selected



def item_action(player, mymonster, target_monster, all_items):
    """
    player: Player オブジェクト（所持アイテム管理）
    mymonster: 自分のモンスター（heal_action を受ける側）
    target_monster: 相手のモンスター（get_action で使う側）
    all_items: {アイテム名: Itemオブジェクト, …}
    """
    while True:
        # 1) アイテム一覧を取得して表示
        items = list(player.item_box.items())  # [("キズぐすり",3), …]
        print("使うアイテムを選ぼう!(Enterを押すと、戻るよ!)")
        for i, (name, cnt) in enumerate(items, start=1):
            print(f"{i}: {name} ({cnt}個)")
        

        # 2) 入力＆バリデーション
        try:
            choice = input(f"1～{len(items)} を選択 > ").strip()
            if not  choice:
                return "continue"
            choice=int(choice)
            if not 1 <= choice <= len(items):
                raise ValueError
           
        except ValueError:
            print("正しい番号を入力してください。")
            continue
        
        

        item_name, _ = items[choice - 1]
        item_obj = all_items[item_name]

        # 3) 回復アイテムなら満タンチェック
        if hasattr(item_obj, "heal_action"):
            if mymonster.stamina >= mymonster._max_stamina:
                print("スタミナは満タンだよ! 別のアイテムを選んでね。")
                continue
            # 満タンでなければ消費＆回復
            player.use_item(item_name)
            item_obj.heal_action(mymonster)
            return "continue"

        # 4) その他アイテムはまず消費
        if not player.use_item(item_name):
            print(f"{item_name} がないよ！別のを選んでね。")
            continue

        # 5) 効果発動
        if hasattr(item_obj, "get_action"):
            item_obj.get_action(target_monster, mymonster, player)
            return "quit"
        elif hasattr(item_obj, "attack_up"):
            item_obj.attack_up(mymonster)
            return "continue"
        elif hasattr(item_obj, "defence_up"):
            item_obj.defence_up(mymonster)
            return "continue"
        else:
            print(f"{item_name} の使い方がわからない…")
            return "quit"




# ── 調整用定数 ──
INITIAL_DROP_RATE    = 0.8   # Lv1のときのドロップ率 80%
DROP_DECAY_PER_LEVEL = 0.015  # レベルが１上がるごとに 5% 減少
MIN_DROP_RATE        = 0.3   # 下限 30%

def drop_item(mymonster, enemy, player):
    # １）レベル差は無視して、自分のレベルだけで計算する場合
    #    prob = INITIAL_DROP_RATE - DROP_DECAY_PER_LEVEL*(mymonster.level-1)
    # ２）下限をかける
    prob = max(MIN_DROP_RATE,
               INITIAL_DROP_RATE - DROP_DECAY_PER_LEVEL * (mymonster.level - 1))

    # 例：Lv1 → 0.80, Lv2 → 0.75, Lv3 → 0.70, … Lv11 → 0.30 (以後ずっと0.30)

    # 確率判定
    if random.random() <= prob:
        item_list    = [attack_potion, defence_potion]
        dropped_item = random.choice(item_list)
        player.add_item(dropped_item)
        print(f"{player.name} は {dropped_item.name} を手に入れた！(Drop率: {prob:.0%})")
    else:
        print(f"アイテムはドロップしなかった…(Drop率: {prob:.0%})")

            
#連続して戦うときに、スタミナが0のままになっている

def select_skill(mymonster):
    """特殊技が使えるときのメニュー選択を返す (1: 通常攻撃, 2: 特殊技)"""
    skill = mymonster.skills[0]
    print("特殊技が使えるぞ！")
    print("1: 通常攻撃")
    print(f"2: {skill._name}")
    while True:
        raw = input("1か2の数字を入力 > ").strip()
        if raw == "":
            print("入力がありません。1か2を入力してください。")
            continue
        if raw not in ("1","2"):
            print("1 か 2 のいずれかを入力してください。")
            continue
        return int(raw)

def game_start(player):
    current = 0
    monster_name=list(player._mymonster_box.keys())
    
    while True:
        name=monster_name[current]
        mymonster=player._mymonster_box[name]
        if mymonster.stamina==0:
            print("\n")
            print("スタミナがないと、たたかえないよ...")
            print("\n")
            action=cannot_fight(player,player._mymonster_box)
            if action=="quit":
                break
        print("戦闘開始!")
        Enemy=randaom_Enemy()
        print(f"{Enemy.name}が現れた！")
        print("\n")
        print(f"行け! {mymonster.name}")
        count=1
        

        while True:
            print("\n")
            print("1:たたかう")
            print("2:にげる")
            print("3:交代")
            print("4:アイテム")
            print("\n")
            choice=input("1~4の中で、選択してくれ")
            if not choice:
                print("何も入力されていません")
                continue
            try:
                choice=int(choice)
            except ValueError:
                print("数字を入力してください")

            if not choice in(1,2,3,4):
                print("\n")
                print("1~4の中で、選択してください")
                continue
           
            if choice==1:
                if count<2:
                    mymonster.attack(Enemy)
                    count+=1
                else: 
                    skiii_choice=select_skill(mymonster)                      
                    if skiii_choice==1:
                        mymonster.attack(Enemy)
                        count+=1
                    else:
                        special_attack=mymonster.skills[0]
                        special_attack.use(mymonster,Enemy)
                        count=1
                        
                time.sleep(0.5)
                if not Enemy.is_dead:
                    Enemy.take_turn(mymonster)
                    
                print(f"{mymonster.name}のスタミナ:{mymonster.stamina}")
                print(f"{Enemy.name}のスタミナ:{Enemy.stamina}")
                if Enemy.is_dead:
                    print(f"{Enemy.name}が倒された！")
                    print("君の勝ちだ!")
                    print("戦闘が終了しました")
                    time.sleep(2)
                    drop_item(mymonster,Enemy,user)
                    mymonster.get_exp(Enemy)
                    player.add_money(100)
                    break
    
                if mymonster.is_dead:
                    print(f"{mymonster.name} が戦闘不能になった")

    # 手持ち全滅かチェック
                    if all(m.is_dead for m in player._mymonster_box.values()):
                        print("負けてしまった")
                        print("あなたの手持ちモンスターはいないようだ。視界が真っ暗になった")
                        print("戦闘が終了しました")
                        player.lose_money(100)
                        break

    # まだ生き残りがいれば交代
                    current += 1
                    mymonster = switch_monster(player._mymonster_box,mymonster)
                    continue
             
            if choice==2:
                print("戦闘が終了しました")
                break

            if choice==3:
                mymonster=switch_monster(player._mymonster_box,mymonster)
                count=1
                


                # print(f"{i}:{m.name} レベル:{m.level} スタミナ:{m.stamina}"for i,m in enumerate(mymonster_box,start=1))
                # この書き方だと、リスト形式等で格納していないため、この連続で出力された塊をどう表示していいか分からない。
                #この連続で出力した、いわば手順書みたいなものを出力するので、中身は見えない。だから、リスト形式で出すか、for文で出すしかない。
            if choice==4:
                action=item_action(player,mymonster,Enemy,all_items)
                if action=="quit":
                    break

            # プレイヤーと敵の行動が一巡したあと：
            for mon in list(player._mymonster_box.values()) + [Enemy]:
                mon.end_of_turn(Enemy)




        
        
                #ここで、インスタンの配列を作っておいて、倒されたら次のインスタンが登場する。もし、インスタンスがいなければ、
                #あなたの手持ちモンスターはいないようだ。視界が真っ暗になった.....を入れたら面白そう
        action=after_finish(player,player._mymonster_box)

        if action=="re_choice":
             action=after_finish(player,player._mymonster_box)

        if action=="quit":
            break






game_start(user)




