import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required

from login_app.models import Monster, UserMonster,TimeAttackRecord,Profile
from services.battle_builder import (
    build_python_mon_from_model,
    build_enemy_instance,
    calc_xp_gain,
)

from battle_engine.status import *
from battle_engine.status import SpecialCooldown



@login_required
def campaign_play(request):
    # 初回 or セッション初期化
    if 'campaign' not in request.session:
        tmpl, _ = Monster.objects.get_or_create(name="リムル")
        um, _ = UserMonster.objects.get_or_create(
            user=request.user,
            template=tmpl,
            defaults={'level': 5, 'experience': 0}
        )
        first = build_python_mon_from_model(tmpl, level=um.level)

        request.session['campaign'] = {
            'party':      [first.to_dict()],
            'active_idx': 0,
            'battle_no':  1,
            'enemy':      build_enemy_instance(level=5).to_dict(),
            'start_time': timezone.now().isoformat(),
        }

    return render(
        request,
        'battle_app/campaign_play.html',
        request.session['campaign']
    )


@require_POST
@login_required
def campaign_action(request):
    data   = json.loads(request.body)
    action = data.get('action')
    target = data.get('target')

    # セッションからステート取得
    st = request.session.get('campaign')
    if not st:
        return HttpResponseBadRequest("セッションが切れています")

    # ─── パーティ再構築（ステータス復元込み） ───
    players = []
    for d in st['party']:
        mon = build_python_mon_from_model(
            Monster.objects.get(name=d['name']),
            level=d['level']
        )
        mon.stamina = d['hp']
        # ステータス復元
        for s in d.get('statuses', []):
            t = s['type']
            if t == 'Burn':
                mon.apply_status(Burn(percent=s['percent'], duration=s['duration']))
            elif t == 'Paralysis':
                mon.apply_status(Paralysis(duration=s['duration']))
            elif t == 'Confusion':
                mon.apply_status(Confusion(duration=s['duration'], chance=s['chance']))
            elif t == 'Regeneration':
                mon.apply_status_regeneration(Regeneration(percent=s['percent'], duration=s['duration']))
            elif t == 'DamageHalf':
                mon.apply_status(DamageHalf(duration=s['duration']))
            elif t == 'Reflection':
                mon.apply_status_myself(Reflection(percent=s['percent'], duration=s['duration']))
            elif t == 'CounterStrike':
                mon.statuses.append(CounterOffense(duration=s['duration'], percent=s['percent']))
            elif t == 'SpecialCooldown':
                mon.apply_status(SpecialCooldown(duration=s['duration']))
        players.append(mon)
    current = players[st['active_idx']]

    # ─── 敵再構築（ステータス復元込み） ───
    ed    = st['enemy']
    enemy = build_python_mon_from_model(
        Monster.objects.get(name=ed['name']),
        level=ed['level']
    )
    enemy.stamina = ed['hp']
    for s in ed.get('statuses', []):
        t = s['type']
        if t == 'Burn':
            enemy.apply_status(Burn(percent=s['percent'], duration=s['duration']))
        elif t == 'Paralysis':
            enemy.apply_status(Paralysis(duration=s['duration']))
        elif t == 'Confusion':
            enemy.apply_status(Confusion(duration=s['duration'], chance=s['chance']))
        elif t == 'Regeneration':
            enemy.apply_status_regeneration(Regeneration(percent=s['percent'], duration=s['duration']))
        elif t == 'DamageHalf':
            enemy.apply_status(DamageHalf(duration=s['duration']))
        elif t == 'Reflection':
            enemy.apply_status_myself(Reflection(percent=s['percent'], duration=s['duration']))
        elif t == 'CounterStrike':
            enemy.statuses.append(CounterOffense(duration=s['duration'], percent=s['percent']))
        elif t == 'SpecialCooldown':
            enemy.apply_status(SpecialCooldown(duration=s['duration']))

    log = []
    bn  = st['battle_no']

    # ─── プレイヤーアクション ───
    if action in ('attack', 'special-attack'):
    # take_my_turn ですべての行動ログを返す
        msgs = current.take_my_turn(action, enemy)
        log.extend(msgs)
    

        print("🔥 Burn付与後のenemy.statuses:", [type(st).__name__ for st in enemy.statuses])

    elif action == 'switch':
        if target is None or target < 0 or target >= len(players):
            return HttpResponseBadRequest('invalid switch')

        party_list = st['party'][:]
        alive_idxs = [i for i, p in enumerate(party_list) if p['hp'] > 0 and i != st['active_idx']]
        if not alive_idxs:
            log.append("交代できるモンスターがいません!")
            return JsonResponse({
                'party':      st['party'],
                'active_idx': st['active_idx'],
                'enemy':      st['enemy'],
                'battle_no':  st['battle_no'],
                'log':        log,
                'finished':   False,
            })
        party_list[0], party_list[target] = party_list[target], party_list[0]
        st['party']      = party_list
        st['active_idx'] = 0
        st['enemy']      = enemy.to_dict()
        request.session['campaign'] = st
        log.append(f"{party_list[0]['name']} に交代！")
        return JsonResponse({
            'party':           st['party'],
            'active_idx':      st['active_idx'],
            'enemy':           st['enemy'],
            'battle_no':       st['battle_no'],
            'log':             log,
            'finished':        False,
            'alive_idxs':      alive_idxs,
        })

    elif action == 'surrender':
        request.session['last_battle_no'] = st['battle_no'] - 1
        request.session.pop('campaign', None)
        UserMonster.objects.filter(user=request.user).delete()
        return JsonResponse({
            'redirect': reverse('battle_app:battle_game_over'),
            'log':      ['降参…']
        })

    else:
        return HttpResponseBadRequest('unknown action')

    # ─── 敵反撃 ───
    if action in ('attack', 'special-attack') and enemy.stamina > 0:
         enemy_msgs = enemy.take_turn(current)
         log.extend(enemy_msgs)

    # ─── 状態異常終了処理 ───
    for p in players:
        for msg in p.end_of_turn(enemy):
            log.append(msg)
    for msg in enemy.end_of_turn(current):
        log.append(msg)

    # ─── 自モン戦闘不能時 ───
    if current.stamina <= 0:
        log.append("自分のモンスターが倒れた！交代してください。")
        alive_idxs = [i for i, p in enumerate(players) if p.stamina > 0 and i != st['active_idx']]
        st['party'] = [p.to_dict() for p in players]
        st['enemy'] = enemy.to_dict()
        request.session['campaign'] = st
        if not alive_idxs:
            log.append("交代できるモンスターがいません！！")
            UserMonster.objects.filter(user=request.user).delete()
            return JsonResponse({
            'redirect': reverse('battle_app:battle_game_over'),
            'log':      log,
            'active_idx':st['active_idx'],
            'party': st['party'],
            'enemy':st['enemy'],
            'battle_no':       st['battle_no'],
        })
            
        return JsonResponse({
            'party':           st['party'],
            'active_idx':      st['active_idx'],
            'enemy':           st['enemy'],
            'battle_no':       st['battle_no'],
            'log':             log,
            'switch_required': True,
            'alive_idxs':      alive_idxs,
        })

    # ─── 全滅判定 ───
    if all(p.stamina <= 0 for p in players):
        log.append("全滅…ゲームオーバー！")
        request.session['last_battle_no'] = st['battle_no']
        request.session.pop('campaign', None)
        return JsonResponse({
            'redirect': reverse('battle_app:battle_game_over'),
            'log':      log,
            'active_idx':st['active_idx'],
            'party':st['party'],
            'enemy':st['enemy'],
        })

    # ─── 敵戦闘不能時 ───
    # ─── 敵撃破判定 ───
    if enemy.stamina <= 0:
        log.append(f"敵 {enemy.name} を撃破！")
        xp = calc_xp_gain(enemy._level)

    # 1) XP を一度だけ付与して、その old/new を記録
        name_to_newlvl = {}
        for um in UserMonster.objects.filter(user=request.user):
            old, new = um.gain_experience(xp)
        # gain_experience 内で save されない場合は um.save() を呼んでください
            um.save()
            log.append(f"{um.template.name} に XP+{xp} (Lv{old}→Lv{new})")
            name_to_newlvl[um.template.name] = new

    # 2) players リストの Python インスタンスにも新レベルを反映
        for p in players:
            if p.name in name_to_newlvl:
                p._level = name_to_newlvl[p.name]

    # 3) セッションに最新情報を書き戻し
        st['party'] = [p.to_dict() for p in players]
        st['enemy'] = enemy.to_dict()

    # 次戦番号計算
        next_bn = st['battle_no'] + 1

    # 10戦クリア判定
        if next_bn > 10:
            request.session['last_battle_no'] = st['battle_no']
        # セッションはそのまま残して clear に飛ばす
            return JsonResponse({
            'redirect':    reverse('battle_app:battle_clear'),
            'log':         log,
            'party':       st['party'],
            'active_idx':  st['active_idx'],
            'enemy':       st['enemy'],
            'battle_no':   st['battle_no'],
        })

    # 仲間化＆次戦準備
        st['battle_no'] = next_bn
        st['recruit']   = {
        'name':   enemy.name,
        'level':  enemy._level,
        'hp':     enemy._max_stamina,
        'max_hp': enemy._max_stamina,
    }
        request.session['campaign'] = st

        return JsonResponse({
        'redirect':    reverse('battle_app:battle_recruit'),
        'log':         log,
        'party':       st['party'],
        'active_idx':  st['active_idx'],
        'enemy':       st['enemy'],
        'battle_no':   st['battle_no'],
    })

    # ─── 戦闘継続（ステータス含めて保存＆返却） ───
    new_party = []
    for p in players:
        entry = p.to_dict()
        entry['statuses'] = []
        for s in p.statuses:
            info = {'type': type(s).__name__, 'duration': s.duration}
            if hasattr(s, 'percent'):
                info['percent'] = s.percent
            if hasattr(s, 'chance'):
                info['chance'] = s.chance
            entry['statuses'].append(info)
        new_party.append(entry)
    st['party'] = new_party

    ed_entry = enemy.to_dict()
    ed_entry['statuses'] = []
    for s in enemy.statuses:
        info = {'type': type(s).__name__, 'duration': s.duration}
        if hasattr(s, 'percent'):
            info['percent'] = s.percent
        
        if hasattr(s, 'chance'):
            info['chance'] = s.chance
        ed_entry['statuses'].append(info)
    st['enemy'] = ed_entry

    request.session['campaign'] = st
    return JsonResponse({
        'party':      st['party'],
        'active_idx': st['active_idx'],
        'enemy':      st['enemy'],
        'battle_no':  st['battle_no'],
        'log':        log,
        'finished':   False,
    })


@login_required
def campaign_recruit(request):
    st  = request.session['campaign']
    rd  = st.get('recruit', {})
    tmpl = get_object_or_404(Monster, name=rd.get('name'))

    skills = []
    if tmpl.skill:
        skills.append({
            'name':   tmpl.skill.name,
            'effect': tmpl.skill.description,
        })

    return render(request, 'battle_app/campaign_recruit.html', {
        'monster': {
            'name':        tmpl.name,
            'level':       rd.get('level'),
            'hp':          rd.get('hp'),
            'max_hp':      rd.get('max_hp'),
            'front_url':   tmpl.image_front.url,
            'back_url':    tmpl.image_back.url,
            'description': tmpl.description,
            'skill_name':  tmpl.skill.name if tmpl.skill else '',
            'skill_desc':  tmpl.skill.description if tmpl.skill else '',
        },
        'skills': skills,
        'party':  st['party'],
    })


@require_POST
@login_required
def campaign_recruit_submit(request):
    user     = request.user
    choice   = request.POST.get('choice')     # 'yes' or 'no'
    drop_idx = request.POST.get('drop_idx')   # 仲間が3体超えた時の「逃がす」 index
    st       = request.session.get('campaign')
    if not st:
        # セッション切れ時は最初からやり直し
        return redirect('battle_app:battle_start')

    # --- 仲間化候補データを取り出し（なければ None） ---
    rd = st.pop('recruit', None)

    # --- 現在のパーティ（セッション）を取得 ---
    party = st.get('party', [])

    # --- choice が 'yes' かつ rd があるときだけ仲間に追加 ---
    if rd and choice == 'yes':
        # 3体以上いるなら drop_idx で escape
        if len(party) >= 3:
            if drop_idx is None:
                return HttpResponseBadRequest('逃がすモンスターを選択してください')
            escape_mon=party.pop(int(drop_idx))
            name = escape_mon['name']
    # これで user と monster name に該当するレコードだけを削除
            UserMonster.objects.filter(
            user=request.user,
            template__name=name
        ).delete()

        # DB 保存：重複防止に get_or_create
        tmpl = get_object_or_404(Monster, name=rd['name'])
        um, created = UserMonster.objects.get_or_create(
            user=user,
            template=tmpl,
            defaults={'level': rd['level'], 'experience': 0},
        )
        if not created:
            # 既に仲間ならレベルだけ上書き
            um.level = rd['level']
            um.save()

        # セッションのパーティに一度だけ追加
        if not any(m['name'] == rd['name'] for m in party):
            party.append({
                'name':      rd['name'],
                'level':     rd['level'],
                'hp':        rd['max_hp'],
                'max_hp':    rd['max_hp'],
                'front_url': tmpl.image_front.url,
                'back_url':  tmpl.image_back.url,
                'attack':    um.template.base_attack,
                'defence':   um.template.base_defence,
            })
    # rd が None or choice != 'yes' の場合はここをスキップ → パーティ変更なし

    # --- 次戦準備（全回復／順序リセット） ---
    st['active_idx'] = 0
    # HP を全回復
    party = [{ **m, 'hp': m['max_hp'] } for m in party]
    st['party']      = party

    bn = st['battle_no']

    # 敵レベル計算
    increments = [0, 2, 3, 4] + [5] * 6
    step       = min(bn - 1, len(increments) - 1)
    next_lvl   = min(party[0]['level'] + increments[step], 20)

    # 敵を再生成
    new_enemy       = build_enemy_instance(level=next_lvl)
    new_enemy.stamina = new_enemy._max_stamina
    st['enemy']     = new_enemy.to_dict()

    

    # セッション書き戻し
    request.session['campaign'] = st

    # 次戦へ
    return redirect('battle_app:battle_start')

@login_required
def campaign_clear(request):
    # セッションから取得＆クリーンアップ
    bt_n = request.session.pop('last_battle_no', None)
    st   = request.session.pop('campaign', {})

    # 仲間データを消す
    UserMonster.objects.filter(user=request.user).delete()

    clear_time = None

    if 'start_time' in st:
        # 1) 経過時間計算
        start_dt = parse_datetime(st['start_time'])
        delta    = timezone.now() - start_dt

        # 2) 全記録テーブルに残す
        new_record = TimeAttackRecord.objects.create(
            user=request.user,
            elapsed_time=delta,
            cleared_at = timezone.now()
        )

        # 3) プロフィールのベスト更新
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.best_record is None or delta < profile.best_record.elapsed_time:
            profile.best_record = new_record
            profile.save(update_fields=['best_record'])

        # 4) クリアタイム文字列化
        total = int(delta.total_seconds())
        hrs, rem  = divmod(total, 3600)
        mins, secs = divmod(rem, 60)
        clear_time = f"{hrs:02d}:{mins:02d}:{secs:02d}"

    return render(request, 'battle_app/campaign_clear.html', {
        'clear_time': clear_time
    })



@login_required
def campaign_game_over(request):
    # ゲームオーバー時に到達したステージ数を取得（なければ 0）
    bt_n = request.session.pop('last_battle_no', 0)
    request.session.pop('campaign', None)
    return render(request, "battle_app/campaign_game_over.html", {
        'bt_n': bt_n,
    })
