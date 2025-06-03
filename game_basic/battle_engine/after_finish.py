from Monster import Monster

from MyMonster import *
from EnemyMonster import EnemyMonster
from item_buy import item_shop


def after_finish(player,monster_box):
    print("\n")
    print("次は何をする？")
    print("\n")
    print("1:次のバトルをする？")
    print("2:一度休憩する？（体力を回復させるよ！）")
    print("3:アイテムショップへ行く")
    print("4:ゲームを終了する")
   
    print("\n")

    try:
        user_option=int(input("1~4の中で選んでね？"))

        if user_option==1:
            return "continue"
        elif user_option==2:
            print(f"{player.name}は休憩した!")
            for mon in monster_box.values():
                # Monster クラスに heal メソッドがあればそれを呼び出す
                mon.heal(mon._max_stamina)
                print(f"{mon.name} の体力が回復した！ (現在: {mon.stamina})")
            return "continue"
        elif user_option==3:
            item_shop(player)
            return "re_choice"
        else:
            print("ゲームを終了しました,引き続きゲームをお楽しみください")
            return "quit"


    except ValueError:
        print("1~4の数字を選択してね!")

    if user_option>4:
        raise ValueError("1~4の数字を選択してね!")


def cannot_fight(player,monster_box):
    print("1:一度休憩して、体力を回復させよう!!）")
    print("2:ゲームを終了する")
    print("\n")

    try:
        user_option=int(input("1~2の中で選んでね？"))

        if user_option==1:
            print(f"{player.name}は休憩した!")
            for mon in monster_box:
                # Monster クラスに heal メソッドがあればそれを呼び出す
                mon.heal(mon._max_stamina)
                print(f"{mon.name} の体力が回復した！ (現在: {mon.stamina})")
            return "continue"
        else:
            print("ゲームを終了しました,引き続きゲームをお楽しみください")
            return "quit"


    except ValueError:
        print("1~2の数字を選択してね!")

    if user_option>3:
        raise ValueError("1~2の数字を選択してね!")
