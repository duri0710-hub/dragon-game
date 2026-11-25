
# app.py

import random
import streamlit as st

from data import CLASSES, CARDS, RELICS
from game import (
    new_game, start_combat, play_card, end_turn,
    select_reward, choose_event, resolve_event,
    rest, buy_relic, save_game, load_game, log
)

st.set_page_config(
    page_title="Dungeon of Chaos",
    page_icon="⚔️",
    layout="wide"
)

# -------------------------
# CSS 디자인
# -------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #100d13, #21131b, #100d13);
    color: #eee5dc;
}

h1, h2, h3 {
    color: #d8ad70 !important;
}

p, label {
    color: #eee5dc;
}

.stButton button {
    background: #38232c;
    color: #f3d8b0;
    border: 1px solid #9c6748;
    border-radius: 10px;
    min-height: 45px;
    transition: 0.2s;
}

.stButton button:hover {
    background: #704333;
    color: white;
    border-color: #d8ad70;
}

.card {
    background: linear-gradient(145deg, #30232c, #17151c);
    border: 1px solid #a77b53;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    min-height: 130px;
    margin-bottom: 10px;
}

.card-title {
    color: #e9bd78;
    font-size: 19px;
    font-weight: bold;
}

.card-description {
    color: #d0c2b4;
    font-size: 13px;
}

.status {
    background: #211a21;
    padding: 14px;
    border: 1px solid #62434a;
    border-radius: 12px;
    text-align: center;
}

.enemy {
    background: #29191e;
    border: 1px solid #9e4444;
    padding: 22px;
    border-radius: 15px;
    text-align: center;
}

hr {
    border-color: #59404a;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# 세션 상태
# -------------------------

if "game" not in st.session_state:
    st.session_state.game = None

if "event" not in st.session_state:
    st.session_state.event = None

if "shop_relic" not in st.session_state:
    st.session_state.shop_relic = "blood_ring"

state = st.session_state.game


# -------------------------
# 공통 화면 함수
# -------------------------

def header():
    st.markdown(
        "<h1 style='text-align:center;'>⚔️ DUNGEON OF CHAOS</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;color:#aa8585;'>"
        "어둠 속에서 살아남아라"
        "</p>",
        unsafe_allow_html=True
    )
    st.divider()


def show_status():
    if not state:
        return

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            f"<div class='status'>❤️ HP<br><b>{state['hp']}/{state['max_hp']}</b></div>",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"<div class='status'>⚡ 에너지<br><b>{state['energy']}/{state['max_energy']}</b></div>",
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"<div class='status'>💰 골드<br><b>{state['gold']}</b></div>",
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"<div class='status'>⭐ 레벨<br><b>{state['level']}</b></div>",
            unsafe_allow_html=True
        )

    with c5:
        st.markdown(
            f"<div class='status'>🏰 구역<br><b>{state['floor']}</b></div>",
            unsafe_allow_html=True
        )


def show_log():
    with st.expander("📜 모험 기록", expanded=False):
        for message in state["log"]:
            st.write("• " + message)


def show_deck():
    with st.expander("🃏 내 덱 보기"):
        st.write(f"전체 카드: {len(state['deck'])}장")

        for card_id in state["deck"]:
            st.write("• " + CARDS[card_id]["name"])

    with st.expander("💎 보유 유물"):
        if not state["relics"]:
            st.write("아직 보유한 유물이 없습니다.")

        for relic_id in state["relics"]:
            relic = RELICS[relic_id]
            st.write(f"**{relic['name']}**")
            st.caption(relic["description"])


# -------------------------
# 메인 화면
# -------------------------

header()

if state:
    show_status()
    st.divider()


# -------------------------
# 시작 화면
# -------------------------

if state is None:

    st.markdown(
        "<h2 style='text-align:center;'>어둠의 던전에 오신 것을 환영합니다</h2>",
        unsafe_allow_html=True
    )

    st.write("")
    st.subheader("직업을 선택하세요")

    cols = st.columns(3)

    descriptions = {
        "전사": "🛡️ 높은 체력과 강력한 공격",
        "마법사": "🔮 강력한 마법과 독",
        "도적": "🗡️ 빠른 공격과 연속 타격"
    }

    for i, job in enumerate(CLASSES):
        with cols[i]:
            st.markdown(
                f"<div class='card'>"
                f"<div class='card-title'>{job}</div>"
                f"<p>{descriptions[job]}</p>"
                f"<p>{CLASSES[job]['description']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

            if st.button(f"{job} 선택", key=f"job_{job}",
                         use_container_width=True):
                st.session_state.game = new_game(job)
                st.rerun()

    st.divider()

    if st.button("💾 저장된 게임 불러오기",
                 use_container_width=True):
        loaded = load_game()

        if loaded:
            st.session_state.game = loaded
            st.rerun()
        else:
            st.warning("저장된 게임이 없습니다.")


# -------------------------
# 게임 진행
# -------------------------

elif state["phase"] == "map":

    st.subheader("🗺️ 던전 탐험")

    st.write(
        f"현재 {state['floor']}구역 | "
        f"탐험한 방: {state['rooms']}개"
    )

    st.info("앞으로 나아갈 장소를 선택하세요.")

    choices = [
        ("⚔️ 일반 전투", "combat"),
        ("❓ 수수께끼 이벤트", "event"),
        ("🔥 휴식 장소", "rest"),
        ("💰 암시장", "shop")
    ]

    for label, kind in choices:
        if st.button(label, use_container_width=True,
                     key=f"map_{kind}"):

            if kind == "combat":
                boss = (
                    state["rooms"] > 0
                    and state["rooms"] % 5 == 4
                )
                start_combat(state, boss=boss)

            elif kind == "event":
                st.session_state.event = choose_event(state)
                state["phase"] = "event"

            elif kind == "rest":
                state["phase"] = "rest"

            elif kind == "shop":
                state["phase"] = "shop"

            st.rerun()


# -------------------------
# 전투 화면
# -------------------------

elif state["phase"] == "combat":

    enemy = state["enemy"]

    st.subheader("⚔️ 전투")

    st.markdown(
        f"<div class='enemy'>"
        f"<h2>👹 {enemy['name']}</h2>"
        f"<h3>❤️ {max(0, enemy['hp'])}/{enemy['max_hp']}</h3>"
        f"<p>☠️ 독: {enemy['poison']}</p>"
        f"<p>예상 공격: {enemy['damage']} 피해</p>"
        f"</div>",
        unsafe_allow_html=True
    )

    st.write("")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("내 체력", state["hp"])
        st.metric("내 방어도", state["block"])

    with c2:
        st.metric("남은 에너지", state["energy"])
        st.metric("남은 카드", len(state["draw_pile"]))

    st.divider()

    st.markdown("### 🃏 손에 든 카드")

    if state["hand"]:

        options = []

        for i, card_id in enumerate(state["hand"]):
            card = CARDS[card_id]
            options.append(
                f"{i+1}. {card['name']} "
                f"(비용 {card['cost']}) - {card['description']}"
            )

        selected = st.selectbox(
            "사용할 카드를 선택하세요",
            range(len(options)),
            format_func=lambda x: options[x]
        )

        if st.button("⚔️ 카드 사용", use_container_width=True):
            play_card(state, selected)
            st.rerun()

    else:
        st.warning("손에 든 카드가 없습니다.")

    st.divider()

    if st.button("⏭️ 턴 종료", use_container_width=True):
        end_turn(state)
        st.rerun()

    st.caption("턴을 종료하면 몬스터가 공격합니다.")

    show_deck()


# -------------------------
# 보상 화면
# -------------------------

elif state["phase"] == "reward":

    st.subheader("🏆 전투 승리!")

    st.success("적을 물리쳤습니다!")
    st.write(f"획득 골드: {state['reward_gold']}")

    st.markdown("### 🃏 새로운 카드 선택")

    cols = st.columns(3)

    for i, card_id in enumerate(state["reward_cards"]):
        card = CARDS[card_id]

        with cols[i]:
            st.markdown(
                f"<div class='card'>"
                f"<div class='card-title'>{card['name']}</div>"
                f"<p>{card['type']}</p>"
                f"<p>{card['description']}</p>"
                f"<p>비용: {card['cost']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

            if st.button("카드 획득", key=f"reward_{i}",
                         use_container_width=True):
                select_reward(state, card_id)
                st.rerun()

    if st.button("카드 없이 진행"):
        state["phase"] = "map"
        st.rerun()


# -------------------------
# 이벤트 화면
# -------------------------

elif state["phase"] == "event":

    event = st.session_state.event

    st.subheader("❓ " + event["title"])
    st.write(event["description"])

    for label, choice in event["choices"]:
        if st.button(label, use_container_width=True):
            resolve_event(state, choice)
            st.session_state.event = None
            st.rerun()


# -------------------------
# 휴식 화면
# -------------------------

elif state["phase"] == "rest":

    st.subheader("🔥 어둠 속의 휴식")
    st.write("잠시 숨을 돌릴 수 있는 장소다.")

    if st.button("체력 25 회복", use_container_width=True):
        rest(state)
        st.rerun()


# -------------------------
# 상점 화면
# -------------------------

elif state["phase"] == "shop":

    st.subheader("💰 암시장")
    st.write(f"보유 골드: {state['gold']}")

    relic_options = {
        key: value["name"]
        for key, value in RELICS.items()
        if key not in state["relics"]
    }

    if relic_options:
        selected_relic = st.selectbox(
            "구매할 유물",
            list(relic_options.keys()),
            format_func=lambda x: relic_options[x]
        )

        st.caption(RELICS[selected_relic]["description"])

        if st.button("유물 구매 (60 골드)"):
            if buy_relic(state, selected_relic):
                st.success("유물을 구매했습니다!")
            else:
                st.error("골드가 부족합니다.")
            st.rerun()

    else:
        st.info("구매할 수 있는 유물이 없습니다.")

    if st.button("체력 회복 (30 골드)"):
        if state["gold"] >= 30:
            state["gold"] -= 30
            state["hp"] = min(
                state["max_hp"], state["hp"] + 20
            )
            st.success("체력 20 회복!")
        else:
            st.error("골드가 부족합니다.")
        st.rerun()

    if st.button("던전으로 돌아가기"):
        state["phase"] = "map"
        st.rerun()


# -------------------------
# 엔딩 화면
# -------------------------

elif state["phase"] == "gameover":

    st.error("💀 GAME OVER")

    st.markdown("### 당신은 던전에서 쓰러졌습니다.")

    st.write(f"직업: {state['job']}")
    st.write(f"도달 구역: {state['floor']}")
    st.write(f"처치한 몬스터: {state['kills']}")

    if st.button("다시 시작"):
        st.session_state.game = None
        st.session_state.event = None
        st.rerun()


elif state["phase"] == "victory":

    st.balloons()

    st.success("🏆 최종 보스 처치 성공!")

    st.markdown("## 던전의 지배자가 되었습니다.")

    st.write(f"직업: {state['job']}")
    st.write(f"레벨: {state['level']}")
    st.write(f"처치한 몬스터: {state['kills']}")

    if st.button("새로운 모험 시작"):
        st.session_state.game = None
        st.rerun()


# -------------------------
# 하단 메뉴
# -------------------------

if state:

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        if st.button("💾 게임 저장", use_container_width=True):
            save_game(state)
            st.success("게임을 저장했습니다!")

    with c2:
        if st.button("📜 모험 기록", use_container_width=True):
            show_log()
