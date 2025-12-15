import random
from typing import Dict, List, Optional

BASE_ROOM_TASKS: Dict[str, List[str]] = {
    "DINING": [
        "ダイニングの椅子の下を掃除して",
        "ダイニングテーブルの下のゴミを拾って",
        "ダイニングのそのコップを片付けて",
        "テーブルの上のそれを渡して",
        "あそこのお皿を運んで",
        #"テーブルの上の『細いやつ』を渡して",
        #"『ここ』に落ちてる紙を捨てる",
        "窓を開けて",
        "窓際の植物に水をあげて",
        "ダイニングの椅子をきれいに並べて",
        "カーテンを閉めて",
        "ダイニングのテーブルを拭いて",
        "テーブルの上の食器を下げて",
        "ダイニングの椅子をきれいに並べて",
        "テーブルにランチョンマットを敷いて",
        "ペンダントライトの明かりを調整して",
    ],
    "LIVING": [
        "リビングのカーテンを開けて",
        "ソファのクッションを整えて",
        "テレビのリモコンを探して",
        "リビングのあの電気をつけて",
        "ソファの横のランプをつけて",
        "そこのライトを消して",
        "扇風機をつけて",
        "扇風機を首振りにして",
        "テーブルの上の紙を渡して",
        "近くのティッシュを渡して",
        "リモコンを探して",
        "ソファの下にある小物を拾って",
        "ソファの上のクッションを持ってきて",
        "テレビをつけて",
        "ソファの上に掃除機をかけて",
        "窓を開けて",
        "カーテンを閉めて",
        "かまどに火をつけて",
        "かまどに木材を補充して",
        "窓のわきにある植物に水をあげて",
        "テーブルの上の黒いやつを持ってきて",
        "机の下を掃除して",
        "机の上の植物に水をあげて",
        "あれを持ってきて",
        "あの人に電話をかけて",
        "じゅうたんを移動して",
        "ソファの横の箱からあれを出して"
    ],
    "BATHROOM": [
        "バスルームのライトをつけて",
        "あのタオルをタオル掛けに戻して",
        "バスルームの換気扇をつけて",
        "そこのコップを洗面台から片付けて",
        "バスルームのドアを閉めて",
        "バスタブにためているお湯を流して",
        "バスタブにお湯をためて",
        "シャワーの水を止めて",
        "バスタブの栓が閉まっているか確認して",
        "シャンプーボトルをそろえて",
        "浴槽のふたを閉めて",
        "バスマットを干して",
    ],
    "BEDROOM": [
        "ベッドわきのライトを消す",
        "寝室の電気を一番明るくして",
        "寝室の窓を開けて",
        "寝室の椅子にある服を運んで",
        "寝室の机の上の本を取ってきて",
        "ベッドメイキングをして",
        "枕をふわっと整えて",
        "昨日読んだ本を持ってきて",
        "本棚の上のライトをつける",
        "引き出しからあれを取ってきて",
        "寝室の暖房をつけて",
        "寝室のクローゼットから赤い服を探して",
        "寝室の布団をきれいにしておいて",
        "寝室のカーテンを閉めて",
        "ベッドの上のクッションを持ってきて",
        "鏡をきれいにして",
        "天井のファンを止めて",
    ],
    "CLOSET": [
        "クローゼットの扉を開けておいて",
        "クローゼットの中のシャツを持ってきて",
        "あの赤い服を探して",
        "あれのハンガーを掛け直して",
        "クローゼットの扉を閉めて",
        "クローゼットの電気を付けて",
        "白いタオルを持ってきて",
        "なんでもいいからジャケットを探して",
        "あの靴を持ってきて",
        "青いやつを探して",
        "クローゼットの照明をつけて",
        "クローゼットのハンガーを整えて",
        "クローゼットの床に置かれた箱を片付けて",
        "収納ケースを引き出して中を確認して",
    ],
    "HALLWAY": [
        "廊下の明かりを消して",
        "廊下のゴミを拾って",
        "廊下に落ちている靴をそろえて",
        "廊下のランナーをまっすぐに直して",
        "『あの辺』のほこりを吸って",
        "廊下のライトを一段暗くして",
        "廊下の端の『それ』を移動して",
        "暖房をつけて",
    ],
    "STAIRS": [
        "階段の電気をつけて",
        "階段を掃除して",
        "階段下の植物に水をあげて",
        "絵を外して持ってきて",
        "階段下のライトを消して",
        "階段下の引き出しからあれを取ってきて",
        "階段の手すりを軽く拭いて",
        "階段の途中にある荷物を片付けて",
        "階段下の収納を確認して",
    ],
    "WASHROOM": [
        "洗面所のタオルを持ってきて",
        "洗濯かごの中のタオルを取ってきて",
        "『あの服』を洗濯かごに入れて",
        "洗面所の『それ』を片付けて",
        "『ここ』のハンドソープを補充して",
        "洗面所の換気扇をつけて",
        "洗面台の『あれ』を戻して",
        "洗面台の鏡を軽く拭いて",
        "洗面台のコップを洗って",
        "タオルを新しいものに交換して",
        "洗面台のライトを点けて",
        "洗濯かごの周りを整えて",
    ],
    "GARAGE": [
        "引き出しからあの工具を持ってきて",
        "ガレージのドアを閉めて",
        "棚のそこにある箱を手前に出して",
        "青いやつの位置を少し右にずらして",
        "茶色いやつの位置を少し左にずらして",
        "ガレージの床の赤いやつを拾って",
        "ガレージからほうきを持ってきて",
        "ガレージの床をほうきがけして",
        "ホースを外して床に置いておいて",
        "棚の上のペンキを床におろして",
        "キャビネットの上の扇風機をつけて",
    ],
    "TOILET": [
        "トイレの換気扇をつけて",
        "トイレのライトを消して",
        "『トイレットペーパー』を補充して",
        "便座のフタを閉めて",
        "トイレのドアを閉めて",
        "『そこ』のマットを整えて",
        "鏡を磨いて",
        "窓を開けて",
        "トイレットペーパーの残量を確認して",
        "トイレの換気扇をつけて",
        "トイレマットを整えて",
        "手洗い場のタオルを交換して",
    ],
    "DOORWAY": [
        "玄関の鍵を閉めて",
        "玄関の近くにある雑誌を運んで",
        "玄関の靴を整えて",
        "『あの靴』を取ってきて",
        "玄関のライトをつけて",
        "傘を持ってきて",
        "玄関脇のあの写真をもってきて",
        "玄関わきの植物に水をあげて",
        "玄関マットのほこりを払って",
        "傘立ての傘をそろえて",
    ],
    "KITCHEN": [
        "パンを焼いて",
        "台所の電気を少し暗くして",
        "キッチンの上のコップを持ってきて",
        "冷蔵庫から『赤いやつ』を取ってきて",
        "シンクの中のフォークを片付けて",
        "コンロの火を止めて",
        "電子レンジを開けて",
        "食洗機の中を確認して",
        "シンクのスポンジをすすいで",
        "『あれ』を冷蔵庫にしまって",
        "冷蔵庫の中のジュースを持ってきて",
        "テーブルの上のスプーンを持ってきて",
        "あれを温めて",
        "キッチンの上のお皿をもってきて",
    ],
    "KIDSROOM": [
        "子供部屋のおもちゃを片付けて",
        "子供部屋の照明をつけて",
        "本棚の絵本をそろえて",
        "学習机の上を整えて",
        "子ども部屋のライトをつけて",
        "『あのおもちゃ』を片付けて",
        "その絵本を持ってきて",
        "水色のやつを持ってきて",
        "子ども部屋の机の上のあれをどけて",
        "『この辺』のブロックを箱に入れて",
        "机の上を掃除して",
    ],
    "BARN": [
        "納屋の窓を開けて換気して",
        "納屋の棚に置かれた道具を整えて",
        "納屋のライトをつけて",
        "納屋の戸を閉めて",
        "工具棚の『それ』を元の場所に戻して",
        "『あのほうき』を入口の近くに立てかけて",
        "納屋の床の『これ』を拾って",
        "干し草の『あれ』を端に寄せて",
        "『この辺』のロープをまとめて",
        "納屋の窓を少し開けて",
        "『あの箱』を手前に出して",
        "エメラルドグリーンの椅子はある？",
        "納屋の床に落ちているものを拾って",
    ],
    "予備室": [
        "部屋のカーテンを開けて",
        "部屋のライトをつけて",
        "机の上のノートをそろえて",
        "部屋の椅子を元の位置に戻して"
    ],
}


ROOM_ALIASES: Dict[str, str] = {
    "リビング": "LIVING",
    "LIVING": "LIVING",
    "LIVINGROOM": "LIVING",
    "LIVING ROOM": "LIVING",
    "ROOM": "LIVING",
    "寝室": "BEDROOM",
    "BEDROOM": "BEDROOM",
    "キッチン": "KITCHEN",
    "KITCHEN": "KITCHEN",
    "ダイニング": "DINING",
    "DINING": "DINING",
    "DININGROOM": "DINING",
    "DINING ROOM": "DINING",
    "廊下": "HALLWAY",
    "HALL": "HALLWAY",
    "HALLWAY": "HALLWAY",
    "階段": "STAIRS",
    "STAIRS": "STAIRS",
    "玄関": "DOORWAY",
    "ENTRANCE": "DOORWAY",
    "DOORWAY": "DOORWAY",
    "洗面所": "WASHROOM",
    "WASHROOM": "WASHROOM",
    "浴室": "BATHROOM",
    "BATHROOM": "BATHROOM",
    "トイレ": "TOILET",
    "TOILET": "TOILET",
    "クローゼット": "CLOSET",
    "CLOSET": "CLOSET",
    "子供部屋": "KIDSROOM",
    "KIDSROOM": "KIDSROOM",
    "ガレージ": "GARAGE",
    "GARAGE": "GARAGE",
    "納屋": "BARN",
    "BARN": "BARN",
    "ROOM1": "予備室",
    "ROOM2": "予備室",
    "ROOM3": "予備室",
    "ROOM4": "予備室",
    "ROOM5": "予備室",
}

DEFAULT_ROOM_TASKS: Dict[str, List[str]] = {
    alias: BASE_ROOM_TASKS[base]
    for alias, base in ROOM_ALIASES.items()
    if base in BASE_ROOM_TASKS
}


def get_tasks_for_room(
    room_name: str,
    tasks_map: Optional[Dict[str, List[str]]] = None,
) -> List[str]:
    """Return the list of tasks associated with the given room name.

    Args:
        room_name: The room identifier selected in the UI. Both Japanese labels
            and room directory names (e.g. ``LIVINGROOM``) are supported.
        tasks_map: Optional mapping that overrides the default task list.

    Returns:
        A list of task strings. Empty when no tasks are registered for the room.
    """

    if not room_name:
        return []

    mapping = tasks_map or DEFAULT_ROOM_TASKS
    normalized = room_name.strip()
    if not normalized:
        return []

    if normalized in mapping:
        return mapping[normalized]

    normalized_upper = normalized.upper()
    if normalized_upper in mapping:
        return mapping[normalized_upper]

    for alias in sorted(ROOM_ALIASES, key=len, reverse=True):
        alias_upper = alias.upper()
        if alias_upper and alias_upper in normalized_upper:
            base = ROOM_ALIASES[alias]
            tasks = (
                mapping.get(alias)
                or mapping.get(alias_upper)
                or mapping.get(base)
                or BASE_ROOM_TASKS.get(base, [])
            )
            if tasks:
                return tasks

    return []


def choose_random_task(
    room_name: str,
    tasks_map: Optional[Dict[str, List[str]]] = None,
) -> Optional[str]:
    """Pick a random task for the specified room.

    Args:
        room_name: The room identifier selected in the UI.
        tasks_map: Optional mapping that overrides the default task list.

    Returns:
        A randomly chosen task string, or ``None`` when no tasks are available.
    """

    tasks = get_tasks_for_room(room_name, tasks_map)
    if not tasks:
        return None
    return random.choice(tasks)
