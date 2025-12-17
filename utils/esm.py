import ast
import re
from copy import deepcopy
from datetime import datetime, timezone

class ExternalStateManager:
    def __init__(self):
        # 1. 既知の初期状態
        self.current_state = {
            "robot_status": {
                "location": "リビングルーム",
                "holding": []
            },
            "environment": {
            "キッチンの棚": [
                "皿",
                "サラダボウル",
                "お椀",
                "木製のボウル",
                "どんぶり",
                "小皿",
                "コップ",
                "ワイングラス",
                "湯呑み",
                "マグカップ",
                "急須",
                "ティーポット",
                "タッパー（保存容器）",
                "コーヒーメーカー",
                "調味料入れ"
            ],
            "キッチンの引き出し": [
                "箸",
                "スプーン",
                "ナイフ",
                "フォーク",
                "おたま",
                "フライ返し",
                "菜箸",
                "ピーラー",
                "栓抜き",
                "缶切り",
                "計量スプーン",
                "ハサミ",
                "剣山",
                "ラップ",
                "アルミホイル",
                "キッチンペーパー"
            ],
            "キッチンシンク" : [
                "水",
                "スポンジ",
                "食器用洗剤",
                "たわし",
                "排水口ネット",
                "シンク用ブラシ"
            ],
            "ダイニングテーブル": [
                "ティッシュ",
                "花瓶の花",
                "ノートパソコン",
                "テーブルクロス",
                "カトラリーケース",
                "リモコン",
                "郵便物",
                "卓上醤油（調味料）"
            ],
            "リビングルーム": [
                "ソファ",
                "クッション",
                "ローテーブル",
                "本棚",
                "本",
                "雑誌",
                "観葉植物",
                "エアコン",
                "空気清浄機",
                "テレビ",
                "DVD",
                "テレビゲーム",
                "ゲーム機本体",
                "スピーカー",
                "Wi-Fiルーター",
                "フロアランプ",
                "ラグ（カーペット）",
                "カーテン",
                "時計",
                "花束"
            ],
            "一番上の棚": [
                "花瓶",
                "アルバム",
                "箱（収納ボックス）",
                "トロフィー",
                "あまり使わない本"
            ],
            "クローゼット": [
                "スーツ",
                "シャツ",
                "Tシャツ",
                "セーター",
                "ズボン",
                "ジーンズ",
                "スカート",
                "ワンピース",
                "コート",
                "パジャマ",
                "キャップ",
                "帽子",
                "ネクタイ",
                "ベルト",
                "バッグ",
                "靴下",
                "下着"
            ],
            "物置": [
                "新聞",
                "スーツケース",
                "ゴルフバッグ",
                "ヒーター",
                "扇風機",
                "掃除機",
                "工具箱",
                "防災グッズ",
                "季節の飾り",
                "キャンプ用品",
                "使わない家電"
            ],
            "玄関": [
                "靴",
                "傘",
                "傘立て",
                "靴箱",
                "スリッパ",
                "鍵",
                "印鑑",
                "宅配ボックス",
                "靴べら"
            ],
            "洗面所": [
                "歯ブラシ",
                "歯磨き粉",
                "コップ",
                "タオル",
                "ハンドソープ",
                "洗顔料",
                "鏡",
                "洗濯機",
                "洗剤",
                "柔軟剤",
                "ドライヤー",
                "体重計"
            ],
            "浴室": [
                "シャンプー",
                "コンディショナー",
                "ボディソープ",
                "風呂椅子",
                "洗面器",
                "バスマット",
                "スポンジ",
                "カミソリ",
                "風呂の蓋",
                "掃除用ブラシ"
            ],
            "トイレ": [
                "トイレットペーパー",
                "トイレブラシ",
                "芳香剤",
                "サニタリーボックス",
                "便座カバー",
                "掃除用シート"
            ],
            "寝室": [
                "ベッド",
                "布団",
                "枕",
                "目覚まし時計",
                "サイドテーブル",
                "間接照明（ランプ）",
                "加湿器",
                "鏡台（ドレッサー）",
                "洋服ダンス"
            ],
            "デスク": [
                "デスクトップパソコン",
                "モニター",
                "キーボード",
                "マウス",
                "卓上ランプ",
                "ペン",
                "ペン立て",
                "ノート",
                "書類",
                "充電ケーブル",
                "ヘッドホン",
                "プリンター",
                "本"
            ],
            "冷蔵庫": [
                "牛乳",
                "卵",
                "野菜",
                "果物",
                "飲み物",
                "お茶",
                "バター",
                "ヨーグルト",
                "ケチャップ",
                "マヨネーズ",
                "冷凍食品",
                "氷"
            ],
            "ベランダ": [
                "洗濯物干し",
                "洗濯バサミ",
                "植木鉢",
                "サンダル",
                "室外機"
            ]
            },
            "known_item_locations": {},
            "open_locations": [],
            "task_goal": {
                "target_location": None,
                "items_needed": {}
            }
        }
        self.state_history: list[dict] = []
        self._record_state_snapshot("initialized")

    def _record_state_snapshot(self, event: str, metadata: dict | None = None) -> None:
        snapshot = {
            "event": event,
            "time": datetime.now(timezone.utc).isoformat(),
            "robot_status": deepcopy(self.current_state.get("robot_status", {})),
            "environment": deepcopy(self.current_state.get("environment", {})),
            "known_locations": deepcopy(self.current_state.get("known_item_locations", {})),
            "open_locations": list(self.current_state.get("open_locations", [])),
        }
        if metadata:
            snapshot["metadata"] = metadata

        if self.state_history:
            last = self.state_history[-1]
            if (
                last.get("robot_status") == snapshot["robot_status"]
                and last.get("environment") == snapshot["environment"]
                and last.get("known_locations") == snapshot["known_locations"]
                and last.get("open_locations") == snapshot["open_locations"]
            ):
                return

        self.state_history.append(snapshot)
    
    def set_task_goal_from_llm(self, goal_description_from_llm):
        """
        [フェーズ1: サブゴール設定]
        LLMとの対話で決定した「タスク目標」をパースして、self.current_state に格納する。
        LLMが "Goal: {target: 'dining_table', items: {'plate': 2}}" のようなJSONを出力
        """
        try:
            # "Goal: " の後の辞書部分 {...} を正規表現で抽出
            match = re.search(r'Goal:\s*(\{.*\})', goal_description_from_llm, re.DOTALL)
            if not match:
                print(f"Error: Could not find 'Goal: {{...}}' pattern in: {goal_description_from_llm}")
                return False

            goal_str = match.group(1)
            # 文字列を安全にPythonの辞書に変換
            goal_dict = ast.literal_eval(goal_str) 
            
            self.current_state['task_goal']['target_location'] = goal_dict.get('target_location')
            self.current_state['task_goal']['items_needed'] = goal_dict.get('items_needed', {})
            print(f"Goal Set: {self.current_state['task_goal']}")
            self._record_state_snapshot(
                "task_goal_updated",
                metadata={"raw": goal_description_from_llm},
            )
            return True # パース成功
        except Exception as e:
            print(f"Error parsing task goal: {e}")
            print(f"Received string: {goal_description_from_llm}")
            return False # パース失敗

    def get_state_as_xml_prompt(self):
        """
        [フェーズ2: 計画]
        現在の self.current_state を、LLMのプロンプトに埋め込むためのXML形式に変換する
        """
        state = self.current_state
        xml_prompt = "<CurrentState>\n"
        xml_prompt += f"  <RobotStatus>\n"
        xml_prompt += f"    <Location>{state['robot_status']['location']}</Location>\n"
        xml_prompt += f"    <Holding>{state['robot_status']['holding']}</Holding>\n"
        xml_prompt += f"  </RobotStatus>\n"
        xml_prompt += f"  <Environment>\n"

        # --- キッチン・ダイニング ---
        xml_prompt += f"    <キッチンの棚>{state['environment']['キッチンの棚']}</キッチンの棚>\n"
        xml_prompt += f"    <キッチンの引き出し>{state['environment']['キッチンの引き出し']}</キッチンの引き出し>\n"
        xml_prompt += f"    <ダイニングテーブル>{state['environment']['ダイニングテーブル']}</ダイニングテーブル>\n"
        xml_prompt += f"    <キッチンシンク>{state['environment']['キッチンシンク']}</キッチンシンク>\n"
        xml_prompt += f"    <冷蔵庫>{state['environment']['冷蔵庫']}</冷蔵庫>\n"

        # --- 居住スペース ---
        xml_prompt += f"    <リビングルーム>{state['environment']['リビングルーム']}</リビングルーム>\n"
        xml_prompt += f"    <寝室>{state['environment']['寝室']}</寝室>\n"
        xml_prompt += f"    <デスク>{state['environment']['デスク']}</デスク>\n"

        # --- 収納 ---
        xml_prompt += f"    <一番上の棚>{state['environment']['一番上の棚']}</一番上の棚>\n"
        xml_prompt += f"    <クローゼット>{state['environment']['クローゼット']}</クローゼット>\n"
        xml_prompt += f"    <物置>{state['environment']['物置']}</物置>\n"

        # --- 水回り・その他 ---
        xml_prompt += f"    <玄関>{state['environment']['玄関']}</玄関>\n"
        xml_prompt += f"    <洗面所>{state['environment']['洗面所']}</洗面所>\n"
        xml_prompt += f"    <浴室>{state['environment']['浴室']}</浴室>\n"
        xml_prompt += f"    <トイレ>{state['environment']['トイレ']}</トイレ>\n"
        xml_prompt += f"    <ベランダ>{state['environment']['ベランダ']}</ベランダ>\n"

        xml_prompt += f"  </Environment>\n"
        xml_prompt += f"  <KnownItemLocations>{state.get('known_item_locations', {})}</KnownItemLocations>\n"
        xml_prompt += f"  <OpenLocations>{state.get('open_locations', [])}</OpenLocations>\n"
        xml_prompt += f"  <TaskGoal>\n"
        xml_prompt += f"    <TargetLocation>{state['task_goal']['target_location']}</TargetLocation>\n"
        xml_prompt += f"    <ItemsNeeded>{state['task_goal']['items_needed']}</ItemsNeeded>\n"
        xml_prompt += f"  </TaskGoal>\n"
        xml_prompt += "  <PlanningHint>\n"
        xml_prompt += "    行動計画（FunctionSequence）で場所やアイテムを指定するときは、current_stateに記載された名称の中から最も似ている語を探して使用してください。\n"
        xml_prompt += "    current_stateに類似した名称が見つからない場合は、その場所やアイテムは環境にないと発話してください。\n"
        xml_prompt += "  </PlanningHint>\n"
        xml_prompt += "</CurrentState>"
        return xml_prompt
    
    def update_state_from_action(self, executed_action_string):
        """
        [フェーズ3: 実行と更新]
        LLMが生成した計画（の1ステップ）を実行した後に呼び出される。
        実行された行動（文字列）をパースし、seld.current_state を更新する。
        これが「状態の逐次更新」の核となる部分です。
        """
        log_messages = []

        def log(message):
            print(message)
            log_messages.append(message)

        log(f"Action Executed: {executed_action_string}")
        action = executed_action_string.strip()
        normalized_action = action.lower()
        state = self.current_state
        robot_status = state.setdefault("robot_status", {})
        environment = state.setdefault("environment", {})
        known_locations = state.setdefault("known_item_locations", {})
        open_locations = state.setdefault("open_locations", [])

        def ensure_holding_list():
            holding = robot_status.get("holding", [])
            if isinstance(holding, list):
                return holding
            if holding:
                robot_status["holding"] = [holding]
            else:
                robot_status["holding"] = []
            return robot_status["holding"]

        def resolve_location(name):
            for existing_location in environment.keys():
                if existing_location.lower() == name.lower():
                    return existing_location
            return name

        def resolve_item(name, location_key=None):
            if location_key:
                for existing_item in environment.get(location_key, []):
                    if existing_item.lower() == name.lower():
                        return existing_item
            for loc, items in environment.items():
                for existing_item in items:
                    if existing_item.lower() == name.lower():
                        return existing_item
            for held_item in ensure_holding_list():
                if held_item.lower() == name.lower():
                    return held_item
            return name

        def remove_from_holding(name):
            holding_items = ensure_holding_list()
            for idx, held_item in enumerate(holding_items):
                if held_item.lower() == name.lower():
                    return holding_items.pop(idx)
            return None

        try:
            if normalized_action.startswith("go to the "):
                match = re.match(r"go to the (.+)", action, re.IGNORECASE)
                if match:
                    requested_location = match.group(1).strip()
                    resolved_location = resolve_location(requested_location)
                    robot_status["location"] = resolved_location
                    log(f"Robot moved to {resolved_location}")
                else:
                    log(f"Could not parse location in action: {action}")

            elif normalized_action.startswith("find "):
                match = re.match(r"find (.+)", action, re.IGNORECASE)
                if match:
                    requested_item = match.group(1).strip()
                    resolved_item = None
                    resolved_location = None
                    for loc, items in environment.items():
                        for candidate in items:
                            if candidate.lower() == requested_item.lower():
                                resolved_item = candidate
                                resolved_location = loc
                                break
                        if resolved_item:
                            break
                    if resolved_item:
                        known_locations[resolved_item] = resolved_location
                        log(f"Found {resolved_item} at {resolved_location}")
                    else:
                        log(f"{requested_item} not found in the environment")
                else:
                    log(f"Could not parse item to find in action: {action}")

            elif normalized_action.startswith("pick up the "):
                match = re.match(r"pick up the (.+)", action, re.IGNORECASE)
                if match:
                    requested_item = match.group(1).strip()
                    current_location = robot_status.get("location")
                    resolved_location = resolve_location(current_location) if current_location else None
                    resolved_item = resolve_item(requested_item, resolved_location)
                    if resolved_location and resolved_item in environment.get(resolved_location, []):
                        environment[resolved_location].remove(resolved_item)
                        ensure_holding_list().append(resolved_item)
                        known_locations.pop(resolved_item, None)
                        log(f"Robot picked up {resolved_item} from {resolved_location}")
                    else:
                        log(f"Item {requested_item} not found at {current_location}")
                else:
                    log(f"Could not parse item to pick up in action: {action}")

            elif normalized_action.startswith("take ") and " from " in normalized_action:
                match = re.match(r"take (.+) from (.+)", action, re.IGNORECASE)
                if match:
                    requested_item = match.group(1).strip()
                    requested_location = match.group(2).strip()
                    resolved_location = resolve_location(requested_location)
                    resolved_item = resolve_item(requested_item, resolved_location)
                    current_location = robot_status.get("location")
                    if current_location and resolved_location.lower() != current_location.lower():
                        log(
                            f"Robot is at {current_location} and cannot take items from {requested_location}"
                        )
                    elif resolved_item in environment.get(resolved_location, []):
                        environment[resolved_location].remove(resolved_item)
                        ensure_holding_list().append(resolved_item)
                        known_locations.pop(resolved_item, None)
                        log(f"Robot took {resolved_item} from {resolved_location}")
                    else:
                        log(f"Item {requested_item} not found in {requested_location}")
                else:
                    log(f"Could not parse take action: {action}")

            elif normalized_action.startswith("put ") and " in the " in normalized_action:
                match = re.match(r"put (.+) in the (.+)", action, re.IGNORECASE)
                if match:
                    requested_item = match.group(1).strip()
                    requested_location = match.group(2).strip()
                    resolved_location = resolve_location(requested_location)
                    current_location = robot_status.get("location")
                    if current_location and resolved_location.lower() != current_location.lower():
                        log(
                            f"Robot is at {current_location} and cannot put items in {requested_location}"
                        )
                    else:
                        resolved_item = resolve_item(requested_item)
                        removed_item = remove_from_holding(resolved_item)
                        if removed_item:
                            environment.setdefault(resolved_location, []).append(removed_item)
                            known_locations[removed_item] = resolved_location
                            log(f"Robot put {removed_item} in the {resolved_location}")
                        else:
                            log(f"Robot is not holding {requested_item}")
                else:
                    log(f"Could not parse put action: {action}")

            elif normalized_action.startswith("open the "):
                match = re.match(r"open the (.+)", action, re.IGNORECASE)
                if match:
                    requested_location = match.group(1).strip()
                    resolved_location = resolve_location(requested_location)
                    if resolved_location not in open_locations:
                        open_locations.append(resolved_location)
                    log(f"Robot opened the {resolved_location}")
                else:
                    log(f"Could not parse location to open in action: {action}")

            elif normalized_action.startswith("close the "):
                match = re.match(r"close the (.+)", action, re.IGNORECASE)
                if match:
                    requested_location = match.group(1).strip()
                    resolved_location = resolve_location(requested_location)
                    if resolved_location in open_locations:
                        open_locations.remove(resolved_location)
                    log(f"Robot closed the {resolved_location}")
                else:
                    log(f"Could not parse location to close in action: {action}")

            elif normalized_action.startswith("hand over ") and " to user" in normalized_action:
                match = re.match(r"hand over (.+) to user", action, re.IGNORECASE)
                if match:
                    requested_item = match.group(1).strip()
                    removed_item = remove_from_holding(requested_item)
                    if removed_item:
                        log(f"Robot handed over {removed_item} to the user")
                    else:
                        log(f"Robot is not holding {requested_item}")
                else:
                    log(f"Could not parse hand over action: {action}")

            elif normalized_action.startswith("push "):
                match = re.match(r"push (.+)", action, re.IGNORECASE)
                if match:
                    pushed_object = match.group(1).strip()
                    log(f"Robot pushed {pushed_object}")
                else:
                    log(f"Could not parse push action: {action}")

            elif normalized_action.startswith("done"):
                log("Task completed.")

            else:
                log(f"Unrecognized action: {action}")

        except Exception as e:
            log(f"State Update Error: {e} on action: {action}")
            # (失敗した場合の処理)

        holding_display = robot_status.get("holding", [])
        log(
            f"State Updated: Robot at {robot_status.get('location')}, holding {holding_display}"
        )

        self._record_state_snapshot(
            "action_update",
            metadata={"action": executed_action_string},
        )

        return "\n".join(log_messages)
