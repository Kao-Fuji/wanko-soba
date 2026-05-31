
# items.py
# わんこそばに流れてくるものをまとめるファイルです。
# クリック回数・出現率・効果はここを触れば変更できます。

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class GameItem:
    key: str
    name: str
    category: str

    # category:
    #   "noodle"  = 食べられる麺
    #   "bad"     = 食べちゃダメ
    #   "effect"  = 効果が出るアイテム

    base_clicks: int = 0
    bowl_color: str = "#f5d7a1"
    weight: int = 10

    # bad用
    penalty: str = ""

    # effect用
    effect_type: str = ""
    effect_value: int = 1

    description: str = ""


ITEMS = [
    GameItem(
        key="soba",
        name="そば",
        category="noodle",
        base_clicks=1,
        bowl_color="#8b5a2b",
        weight=25,
        description="基本のわんこそば。1回で食べられる。",
    ),
    GameItem(
        key="udon",
        name="うどん",
        category="noodle",
        base_clicks=3,
        bowl_color="#f6e7c1",
        weight=18,
        description="太めなので3回クリック。",
    ),
    GameItem(
        key="ramen",
        name="中華麺",
        category="noodle",
        base_clicks=5,
        bowl_color="#ffd45a",
        weight=14,
        description="つるつるしているけど5回クリック。",
    ),
    GameItem(
        key="houtou",
        name="ほうとう",
        category="noodle",
        base_clicks=10,
        bowl_color="#e88932",
        weight=8,
        description="重い。10回クリック。",
    ),

    GameItem(
        key="dark_matter",
        name="ダークマター",
        category="bad",
        bowl_color="#1f1b2e",
        weight=6,
        penalty="game_over",
        description="食べたら一発アウト。",
    ),
    GameItem(
        key="rock",
        name="岩",
        category="bad",
        bowl_color="#777777",
        weight=7,
        penalty="minus_bowls",
        description="食べるとお椀が3個減る。",
    ),

    GameItem(
        key="rock_salt",
        name="岩塩",
        category="effect",
        bowl_color="#cde8ff",
        weight=7,
        effect_type="multiply",
        effect_value=2,
        description="食べると、しばらく必要クリック数が2倍。",
    ),
    GameItem(
        key="moss",
        name="苔",
        category="effect",
        bowl_color="#3c8a3c",
        weight=5,
        effect_type="multiply",
        effect_value=3,
        description="食べると、しばらく必要クリック数が3倍。",
    ),
    GameItem(
        key="yakumi",
        name="薬味",
        category="effect",
        bowl_color="#9bd44e",
        weight=10,
        effect_type="one_click",
        effect_value=1,
        description="食べると、しばらく全部1回で食べられる。",
    ),
]


ITEM_BY_KEY = {item.key: item for item in ITEMS}


def choose_random_item():
    """
    出現率 weight に従って、次のアイテムを1つ選ぶ。
    """
    return random.choices(
        ITEMS,
        weights=[item.weight for item in ITEMS],
        k=1
    )[0]


def get_item(key):
    """
    keyからアイテム設定を取り出す。
    """
    return ITEM_BY_KEY[key]


def calc_required_clicks(item, active_effect):
    """
    今の効果を考慮して、そのアイテムに必要なクリック数を返す。
    active_effect は screen_game.py 側で管理します。
    """
    if item.category != "noodle":
        return 0

    if active_effect is None:
        return item.base_clicks

    effect_type = active_effect.get("type")

    if effect_type == "multiply":
        return item.base_clicks * active_effect.get("value", 1)

    if effect_type == "one_click":
        return 1

    return item.base_clicks