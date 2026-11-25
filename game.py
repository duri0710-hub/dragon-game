
# game.py

import random
import json
import os

from data import CLASSES, CARDS, ENEMIES, BOSSES, RELICS

SAVE_PATH = "saves/savegame.json"


def new_game(job):
    player = CLASSES[job]

    return {
        "job": job,
        "hp": player["hp"],
        "max_hp": player["hp"],
        "energy": player["energy"],
        "max_energy": player["energy"],
        "gold": 50,
        "level": 1,
        "exp": 0,
        "exp_next": 40,
        "deck": player["deck"].copy(),
        "draw_pile": [],
        "hand": [],
        "discard": [],
        "relics": [],
        "block": 0,
        "kills": 0,
        "rooms": 0,
        "floor": 1,
        "phase": "map",
        "enemy": None,
        "log": ["어둠의 던전에 입장했다."],
        "reward_cards": [],
        "reward_gold": 0,
        "map_choices": ["전투", "이벤트", "휴식"]
    }


def log(state, message):
    state["log"].insert(0, message)
    state["log"] = state["log"][:12]


def shuffle_deck(state):
    state["draw_pile"] = state["deck"].copy()
    random.shuffle(state["draw_pile"])
    state["discard"] = []


def draw_cards(state, amount):
    for _ in range(amount):
        if not state["draw_pile"]:
            if not state["discard"]:
                break

            state["draw_pile"] = state["discard"].copy()
            random.shuffle(state["draw_pile"])
            state["discard"] = []

        state["hand"].append(state["draw_pile"].pop())


def start_combat(state, boss=False):
    if boss:
        index = min((state["floor"] // 5) - 1, len(BOSSES) - 1)
        enemy = BOSSES[max(0, index)].copy()
    else:
        enemy = random.choice(ENEMIES).copy()

    enemy["max_hp"] = enemy["hp"]
    enemy["poison"] = 0

    state["enemy"] = enemy
    state["block"] = 0
    state["energy"] = state["max_energy"]
    state["hand"] = []

    shuffle_deck(state)
    draw_cards(state, 5)

    if "blood_ring" in state["relics"]:
        state["hp"] = min(state["max_hp"], state["hp"] + 5)

    state["phase"] = "combat"
    log(state, f"{enemy['name']}이(가) 나타났다!")


def play_card(state, index):
    if state["phase"] != "combat":
        return

    if index < 0 or index >= len(state["hand"]):
        return

    card_id = state["hand"][index]
    card = CARDS[card_id]
    enemy = state["enemy"]

    cost = card["cost"]

    if state["energy"] < cost:
        log(state, "에너지가 부족하다!")
        return

    state["energy"] -= cost

    damage = card.get("damage", 0)

    if damage:
        if "demon_eye" in state["relics"]:
            damage += 2

        enemy["hp"] -= damage
        log(state, f"{card['name']} 사용! {damage} 피해!")

    block = card.get("block", 0)

    if block:
        state["block"] += block
        log(state, f"방어도 {block} 획득!")

    poison = card.get("poison", 0)

    if poison:
        enemy["poison"] += poison
        log(state, f"적에게 독 {poison} 부여!")

    draw = card.get("draw", 0)

    if draw:
        draw_cards(state, draw)
        log(state, f"카드 {draw}장 드로우!")

    state["hand"].pop(index)
    state["discard"].append(card_id)

    if enemy["hp"] <= 0:
        win_combat(state)
        return


def enemy_turn(state):
    enemy = state["enemy"]

    if enemy["poison"] > 0:
        poison_damage = enemy["poison"]
        enemy["hp"] -= poison_damage
        enemy["poison"] = max(0, enemy["poison"] - 1)

        log(state, f"독 피해 {poison_damage}!")

        if enemy["hp"] <= 0:
            win_combat(state)
            return

    attack = enemy["damage"]

    damage = max(0, attack - state["block"])
    state["hp"] -= damage

    log(state, f"{enemy['name']}의 공격! {damage} 피해!")

    state["block"] = 0

    if state["hp"] <= 0:
        state["hp"] = 0
        state["phase"] = "gameover"
        log(state, "당신은 어둠에 삼켜졌다.")
        return

    start_turn(state)


def start_turn(state):
    state["energy"] = state["max_energy"]
    state["block"] = 0

    if "iron_heart" in state["relics"]:
        state["block"] += 3

    draw_cards(state, 5)

    log(state, "새로운 턴이 시작되었다.")


def end_turn(state):
    if state["phase"] != "combat":
        return

    state["discard"].extend(state["hand"])
    state["hand"] = []

    enemy_turn(state)


def win_combat(state):
    enemy = state["enemy"]

    exp = enemy["exp"]
    gold = random.randint(15, 25)

    if "ancient_coin" in state["relics"]:
        gold += 10

    state["exp"] += exp
    state["gold"] += gold
    state["kills"] += 1
    state["rooms"] += 1

    log(state, f"승리! 경험치 {exp}, 골드 {gold} 획득!")

    if state["exp"] >= state["exp_next"]:
        state["exp"] -= state["exp_next"]
        state["level"] += 1
        state["exp_next"] += 30
        state["max_hp"] += 5
        state["hp"] = min(state["max_hp"], state["hp"] + 10)

        log(state, "레벨 업! 최대 체력 5 증가!")

    state["reward_gold"] = gold
    state["reward_cards"] = random.sample(
        list(CARDS.keys()), 3
    )

    state["phase"] = "reward"

    # 5층마다 보스 처치 후 다음 구역으로 진행
    if state["rooms"] % 5 == 0:
        if state["floor"] >= 10:
            state["phase"] = "victory"
            log(state, "최종 보스를 물리쳤다!")
        else:
            state["floor"] += 1
            log(state, "새로운 구역이 열렸다!")


def select_reward(state, card_id):
    state["deck"].append(card_id)
    state["phase"] = "map"
    log(state, f"{CARDS[card_id]['name']} 카드를 획득했다.")


def choose_event(state):
    events = [
        {
            "title": "수상한 제단",
            "description": "제단에서 붉은 빛이 흘러나온다.",
            "choices": [
                ("피를 바친다 (체력 15 소모, 골드 40 획득)", "blood"),
                ("제단을 떠난다", "leave")
            ]
        },
        {
            "title": "잊혀진 보물",
            "description": "오래된 상자가 발견되었다.",
            "choices": [
                ("상자를 연다 (골드 30 획득)", "treasure"),
                ("무시한다", "leave")
            ]
        }
    ]

    return random.choice(events)


def resolve_event(state, choice):
    if choice == "blood":
        if state["hp"] > 15:
            state["hp"] -= 15
            state["gold"] += 40
            log(state, "피를 바치고 골드 40을 얻었다.")
        else:
            log(state, "체력이 부족해 제단을 이용할 수 없다.")

    elif choice == "treasure":
        state["gold"] += 30
        log(state, "골드 30을 획득했다.")

    else:
        log(state, "아무 일도 일어나지 않았다.")

    state["phase"] = "map"


def rest(state):
    heal = min(25, state["max_hp"] - state["hp"])
    state["hp"] += heal
    state["phase"] = "map"
    log(state, f"휴식으로 체력 {heal} 회복!")


def buy_relic(state, relic_id):
    cost = 60

    if state["gold"] < cost:
        return False

    if relic_id in state["relics"]:
        return False

    state["gold"] -= cost
    state["relics"].append(relic_id)

    log(state, f"{RELICS[relic_id]['name']} 획득!")
    return True


def save_game(state):
    os.makedirs("saves", exist_ok=True)

    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_game():
    if not os.path.exists(SAVE_PATH):
        return None

    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)

        return state
    except (OSError, ValueError):
        return None
