
# data.py

CLASSES = {
    "전사": {
        "hp": 100,
        "energy": 3,
        "description": "높은 체력과 강력한 물리 공격",
        "deck": [
            "strike", "strike", "strike",
            "defend", "defend", "defend",
            "heavy", "heavy", "battle_cry"
        ]
    },
    "마법사": {
        "hp": 75,
        "energy": 3,
        "description": "마법과 상태 이상으로 적을 제압",
        "deck": [
            "fireball", "fireball", "strike",
            "defend", "defend", "mana_burst",
            "poison", "meditate", "meditate"
        ]
    },
    "도적": {
        "hp": 85,
        "energy": 3,
        "description": "빠른 연속 공격과 독을 사용",
        "deck": [
            "strike", "strike", "defend",
            "defend", "poison", "poison",
            "quick_stab", "quick_stab", "battle_cry"
        ]
    }
}

CARDS = {
    "strike": {
        "name": "강철 베기",
        "cost": 1,
        "type": "공격",
        "damage": 8,
        "description": "적에게 8의 피해"
    },
    "defend": {
        "name": "철벽 방어",
        "cost": 1,
        "type": "방어",
        "block": 8,
        "description": "방어도 8 획득"
    },
    "heavy": {
        "name": "처형자의 일격",
        "cost": 2,
        "type": "공격",
        "damage": 20,
        "description": "적에게 20의 피해"
    },
    "fireball": {
        "name": "암흑 화염구",
        "cost": 2,
        "type": "공격",
        "damage": 18,
        "description": "적에게 18의 마법 피해"
    },
    "mana_burst": {
        "name": "마나 폭발",
        "cost": 1,
        "type": "공격",
        "damage": 12,
        "description": "적에게 12의 피해"
    },
    "poison": {
        "name": "맹독 투척",
        "cost": 1,
        "type": "스킬",
        "poison": 4,
        "description": "적에게 독 4 부여"
    },
    "quick_stab": {
        "name": "그림자 찌르기",
        "cost": 0,
        "type": "공격",
        "damage": 5,
        "description": "적에게 5의 피해"
    },
    "battle_cry": {
        "name": "전투 함성",
        "cost": 1,
        "type": "스킬",
        "block": 5,
        "draw": 1,
        "description": "방어도 5 획득 및 카드 1장 드로우"
    },
    "meditate": {
        "name": "명상",
        "cost": 1,
        "type": "스킬",
        "block": 4,
        "draw": 2,
        "description": "방어도 4 획득 및 카드 2장 드로우"
    }
}

ENEMIES = [
    {
        "name": "타락한 고블린",
        "hp": 32,
        "damage": 8,
        "exp": 15
    },
    {
        "name": "망령 기사",
        "hp": 45,
        "damage": 11,
        "exp": 22
    },
    {
        "name": "심연의 사냥개",
        "hp": 38,
        "damage": 13,
        "exp": 20
    },
    {
        "name": "저주받은 기사",
        "hp": 60,
        "damage": 14,
        "exp": 30
    }
]

BOSSES = [
    {
        "name": "혈월의 기사",
        "hp": 120,
        "damage": 18,
        "exp": 100
    },
    {
        "name": "심연의 군주",
        "hp": 180,
        "damage": 24,
        "exp": 200
    }
]

RELICS = {
    "blood_ring": {
        "name": "피의 반지",
        "description": "전투 시작 시 체력 5 회복"
    },
    "iron_heart": {
        "name": "강철 심장",
        "description": "매 턴 시작 시 방어도 3 획득"
    },
    "demon_eye": {
        "name": "악마의 눈",
        "description": "모든 공격 피해 2 증가"
    },
    "ancient_coin": {
        "name": "고대의 동전",
        "description": "전투 승리 시 골드 10 추가 획득"
    }
}
