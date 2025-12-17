import json
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
import yaml
from pages.consent import (
    apply_sidebar_hiding,
    configure_page,
    require_consent,
    should_hide_sidebar,
)
from dotenv import load_dotenv

from utils.api import build_bootstrap_user_message, client
from archive.jsonl import (
    record_task_duration,
    save_conversation_history_to_firestore
)
from utils.run_and_show import show_function_sequence
from archive.image_task_sets import extract_task_lines
from utils.esm import ExternalStateManager
from utils.evaluation_form import render_standard_evaluation_form

PROMPT_GROUP = "smalltalk"
NEXT_PAGE = None
REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_TASKINFO_PATH = REPO_ROOT / "prompts" / "prompt_taskinfo_sets.yaml"
_PROMPT_TASKINFO_CACHE: dict[str, dict[str, str]] | None = None

IMAGE_TITLE_MAP: dict[str, list[str]] = {
    "dining": [
        "1 食器だけセッティングした様子",
        "2 大皿料理を囲む様子",
        "3 花を飾った和食の食卓",
        "4 お盆で和定食",
        "5 子供がいる家庭のソファダイニング",
    ],
    "flower": [
        "1 窓辺",
        "2 ダイニングテーブル",
        "3 リビングのローテーブル",
        "4 玄関",
        "5 廊下",
    ],
}


def load_prompt_taskinfo_sets() -> dict[str, dict[str, str]]:
    global _PROMPT_TASKINFO_CACHE
    if _PROMPT_TASKINFO_CACHE is None:
        with PROMPT_TASKINFO_PATH.open(encoding="utf-8") as f:
            _PROMPT_TASKINFO_CACHE = yaml.safe_load(f)
    return _PROMPT_TASKINFO_CACHE


def get_prompt_options(prompt_group: str) -> dict[str, dict[str, str]]:
    return {
        key: value
        for key, value in load_prompt_taskinfo_sets().items()
        if value.get("prompt_group") == prompt_group
    }


def _get_image_title(task_name: str, index: int) -> str:
    if not task_name:
        return f"{index:02d}: {index}"
    titles = IMAGE_TITLE_MAP.get(task_name.lower())
    if titles and 1 <= index <= len(titles):
        return titles[index - 1]
    return f"{index:02d}: {index}"


def _render_task_image_picker(image_paths: list[str], task_name: str) -> None:
    if not image_paths:
        return

    st.markdown("上記のタスクが完了した状態を想像し、写真からイメージに近いものを選んでください。")
    columns = st.columns(len(image_paths))
    for idx, (col, image_path) in enumerate(zip(columns, image_paths), start=1):
        resolved_path = (REPO_ROOT / image_path).resolve()
        title = _get_image_title(task_name, idx)
        with col:
            st.image(str(resolved_path), use_container_width=True)
            st.caption(title)

    image_options = list(range(1, len(image_paths) + 1))
    if not image_options:
        return

    selection_key = "2_image_selection"
    if selection_key not in st.session_state:
        st.session_state[selection_key] = image_options[0]

    st.radio(
        "1~5の中からイメージに近いものを選んでください",
        image_options,
        horizontal=True,
        key=selection_key,
    )

load_dotenv()


configure_page(hide_sidebar_for_participant=True)


def _reset_conversation_state(system_prompt: str) -> None:
    """Reset conversation-related session state for experiment 2."""

    # 1. ESM（状態）の初期化
    st.session_state.esm = ExternalStateManager() 
    
    # 2. 実行すべき行動計画のキュー（名前を action_plan_queue に統一）
    st.session_state.action_plan_queue = [] 
    
    # 3. フェーズ1（目標設定）が完了したかのフラグ
    st.session_state.goal_set = False 
    
    # 4. システムプロンプトを「テンプレート」として保持
    #    (LLM呼び出しの度に {current_state_xml} を埋め込むため)
    st.session_state.system_prompt_template = system_prompt 
    
    # 5. contextは「空」で開始する
    st.session_state.context = [] 
    
    # --- 以下は既存のリセットロジック ---
    st.session_state.active = True
    st.session_state.conv_log = {
        "label": "",
        "clarifying_steps": []
    }
    st.session_state.saved_jsonl = []
    st.session_state.turn_count = 0
    st.session_state.force_end = False
    st.session_state["chat_input_history"] = []
    st.session_state["experiment_followup_prompt"] = False
    st.session_state.pop("experiment_followup_choice", None)
    st.session_state.pop("task_timer_started_at", None)
    st.session_state.pop("task_duration_recorded", None)
    _update_random_task_selection(
        "experiment_selected_task_label",
        "experiment_task_labels",
        "experiment_label_to_key",
        "experiment_selected_task_set",
    )

def _update_random_task_selection(label_key: str, labels_key: str, mapping_key: str, set_key: str) -> None:
    """Select a new task label at random and update related session state."""

    labels = st.session_state.get(labels_key) or []
    if not labels:
        return

    current_label = st.session_state.get(label_key)
    candidates = [label for label in labels if label != current_label] or labels
    new_label = random.choice(candidates)

    st.session_state[label_key] = new_label
    label_to_key = st.session_state.get(mapping_key) or {}
    st.session_state[set_key] = label_to_key.get(new_label)

TAG_RE = re.compile(r"</?([A-Za-z0-9_]+)(\s[^>]*)?>")

def strip_tags(text: str) -> str:
    return TAG_RE.sub("", text or "").strip()

def extract_between(tag: str, text: str) -> str | None:
    match = re.search(fr"<{tag}>([\s\S]*?)</{tag}>", text or "", re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_xml_tag(xml_string, tag_name):
    """指定されたタグの内容を抽出する"""
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    match = re.search(pattern, xml_string, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None

def parse_function_sequence(sequence_str):
    """FunctionSequenceの番号付きリストをパースする"""
    if not sequence_str:
        return []
    # "1. go to..." "2. pick up..." などを抽出
    actions = re.findall(r'^\s*\d+\.\s*(.*)', sequence_str, re.MULTILINE)
    return [action.strip() for action in actions]

def safe_format_prompt(template: str, **kwargs) -> str:
    # {current_state_xml},{house},{room} だけを置換し、他の { ... } は触らない
    pattern = re.compile(r"\{(current_state_xml|house|room)\}")
    return pattern.sub(lambda m: str(kwargs.get(m.group(1), m.group(0))), template)


def _append_context_message(context: list[dict], message: dict) -> None:
    stamped = dict(message)
    stamped.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    if stamped.get("role") == "assistant" and "spoken_response" not in stamped:
        content = stamped.get("content")
        if isinstance(content, str):
            stamped["spoken_response"] = content
    context.append(stamped)

def run_plan_and_show(reply: str):
    """<Plan> ... </Plan> を見つけて実行し、結果を表示"""
    plan_match = re.search(r"<Plan>(.*?)</Plan>", reply, re.S)
    if not plan_match:
        return
    steps = re.findall(r"<Step>(.*?)</Step>", plan_match.group(1))
    if not steps:
        return

    with st.expander("Plan 実行ログ", expanded=True):
        for step in steps:
            try:
                result = eval(step)  # 例: move_to(1.0, 2.0)
                st.write(f"✅ `{step}` → **{result}**")
            except Exception as e:
                st.write(f"⚠️ `{step}` の実行でエラー: {e}")

def finalize_and_render_plan(label: str):
    """会話終了時に行動計画をまとめて画面表示"""
    # final_answer の決定
    last_assistant = next((m for m in reversed(st.session_state.context) if m["role"] == "assistant"), None)
    final_answer = extract_between("FinalAnswer", last_assistant["content"]) if last_assistant else None
    if not final_answer and last_assistant:
        final_answer = strip_tags(last_assistant["content"])

    st.session_state.conv_log["final_answer"] = final_answer or ""
    st.session_state.conv_log["label"] = "sufficient" if label == "sufficient" else "insufficient"

    # question_label が None のステップは継続が無ければ insufficient で埋める
    for s in st.session_state.conv_log["clarifying_steps"]:
        if s["question_label"] is None:
            s["question_label"] = "insufficient"

    st.subheader("会話サマリ（JSON）")
    st.code(
        json.dumps(st.session_state.conv_log, ensure_ascii=False, indent=2),
        language="json"
    )

def app():
    # require_consent()
    st.markdown("### 雑談型")

    # if should_hide_sidebar():
    #     apply_sidebar_hiding()

    prompt_options = get_prompt_options(PROMPT_GROUP)
    if not prompt_options:
        st.error("指定されたプロンプトグループに対応するプロンプトが見つかりませんでした。")
        return

    prompt_keys = list(prompt_options.keys())
    prompt_label_state_key = f"experiment_{PROMPT_GROUP}_prompt_label"
    if prompt_label_state_key not in st.session_state:
        st.session_state[prompt_label_state_key] = random.choice(prompt_keys)

    default_prompt_label = st.session_state[prompt_label_state_key]
    st.markdown("#### ①プロンプト選択（自動）")
    prompt_label = st.selectbox(
        "選択肢",
        prompt_keys,
        index=prompt_keys.index(default_prompt_label)
        if default_prompt_label in prompt_keys
        else 0,
    )
    selected_prompt = prompt_options[prompt_label]
    system_prompt = selected_prompt.get("prompt", "")
    selected_task_name = selected_prompt.get("task", "")
    selected_taskinfo = selected_prompt.get("taskinfo", "")
    image_candidates = selected_prompt.get("image_candidates") or []

    if not system_prompt:
        st.error("プロンプトの内容が設定されていません。JSONファイルを確認してください。")
        return

    st.session_state[prompt_label_state_key] = prompt_label
    st.session_state["prompt_label"] = prompt_label
    st.session_state["prompt_group"] = PROMPT_GROUP

    payload = {}

    house = payload.get("house") if isinstance(payload, dict) else ""
    room = payload.get("room") if isinstance(payload, dict) else ""
    meta_lines = []

    task_lines = extract_task_lines(payload)

    st.markdown("#### ②指定されたタスク")
    st.caption("下のタスクをそのまま画面下部のチャットに入力してください。")
    if selected_taskinfo:
        st.info(selected_taskinfo)
    else:
        st.info("タスクが登録されていません。")

    _render_task_image_picker(image_candidates, selected_task_name)
    st.warning("ロボットは、これらの画像の情報は持っていません。あくまでイメージを掴むための参考としてご利用ください。")

    # if task_lines:
    #     for line in task_lines:
    #         st.info(f"{line}")
    # else:
    #     st.info("タスクが登録されていません。")

    # 1) セッションにESMとコンテキストを初期化
    if (
        "esm" not in st.session_state
        or st.session_state.get("system_prompt_template") != system_prompt
    ):
        _reset_conversation_state(system_prompt) 

    # セッションからESMオブジェクトを取得
    esm = st.session_state.esm
    
    if "active" not in st.session_state:
        st.session_state.active = True
    if "turn_count" not in st.session_state:
        st.session_state.turn_count = 0
    if "force_end" not in st.session_state:
        st.session_state.force_end = False
    if "chat_input_history" not in st.session_state:
        st.session_state["chat_input_history"] = []
    if "experiment_followup_prompt" not in st.session_state:
        st.session_state["experiment_followup_prompt"] = False

    context = st.session_state.context
    esm = st.session_state.esm
    queue = st.session_state.action_plan_queue
    current_state = esm.current_state
    should_stop = False
    end_message = ""

    tab_conversation, tab_state = st.tabs([
        "ロボットとの会話",
        "現在の状態",
    ])

    with tab_conversation:
        st.markdown("#### ③ロボットとの会話")
        st.caption(
            """
            最初に②のタスクを入力し、ロボットと自然に会話してください。
            最終的にはロボットと協力してタスクを達成させることが目標ですが、タスクに関係ない会話や指示もすることができます。
            """
        )

        if selected_taskinfo:
            st.info(selected_taskinfo)
        else:
            st.info("タスクが登録されていません。")

        # 2. 既存の会話履歴を表示
        for msg in context:
            if msg["role"] == "system":
                continue
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                # 既存のヘルパー関数をそのまま利用
                if msg["role"] == "assistant":
                    reply_xml = msg.get("full_reply", msg.get("content", ""))
                    show_function_sequence(reply_xml)
                    # show_spoken_response(reply_xml)

        # 3. [フェーズ2: 実行ループ] 実行すべき行動計画（キュー）があるか？
        if queue:
            next_action = queue[0]
            st.info(f"次の行動計画: **{next_action}**")

            # 実行ボタン
            if st.button(f"▶️ 実行: {next_action}", key="run_next_step", type="primary"):
                action_to_run = queue.pop(0)  # キューの先頭を取り出す
                st.session_state.action_plan_queue = queue  # キューを更新

                # [!!!] ここで実際のロボットAPIを呼び出す（代わりにESMを更新）[!!!]
                with st.spinner(f"実行中: {action_to_run}..."):
                    # time.sleep(1) # import time が必要
                    execution_log = esm.update_state_from_action(action_to_run)

                # 実行結果を会話履歴（コンテキスト）に追加
                exec_details = execution_log or "ロボットの状態を更新しました。"
                exec_msg = f"（実行完了: {action_to_run}。\n{exec_details}）"
                _append_context_message(
                    context,
                    {"role": "user", "content": exec_msg},
                )  # 実行結果をLLMに伝える
                st.chat_message("user").write(exec_msg)

                # キューが空になったら、LLMに次の計画を尋ねる
                if not queue:
                    st.info("サブタスクが完了しました。LLMに次の計画を問い合わせます...")
                    # LLMが次の計画を生成すべきことを示す特殊なフラグを設定
                    st.session_state.next_plan_request = "現在のタスク目標に基づき、現在の状態から次のサブタスクの行動計画（FunctionSequence）を生成してください。"
                    st.session_state.trigger_llm_call = True
                st.rerun() # 画面を再描画して次のステップを表示

        # 4. LLM呼び出しのトリガー（ユーザー入力 or 計画完了）
        user_input = None
        if not st.session_state.get("force_end"):
            user_input = st.chat_input(
                "ロボットへの回答を入力してください",
                key="experiment_2_chat_input",
            )
            if user_input:
                st.session_state["chat_input_history"].append(user_input)
                st.session_state.trigger_llm_call = True

                # ユーザーが入力した=既存の計画に介入した→したがって古い行動計画（キュー）を破棄する
                if queue:
                    st.warning("ユーザーが介入しました。既存の行動計画を破棄します。")
                    st.session_state.action_plan_queue = []
                    queue = []

        # 5. [フェーズ1 & 2: LLM呼び出し]
        if st.session_state.get("trigger_llm_call"):
            st.session_state.trigger_llm_call = False  # フラグをリセット

            # [変更点] ユーザー入力があった場合のみコンテキストに追加
            if user_input:
                _append_context_message(
                    context,
                    {"role": "user", "content": user_input},
                )

            # [!!!] LLM呼び出しのコアロジック [!!!]
            with st.chat_message("assistant"):
                with st.spinner("ロボットが考えています..."):
                    # (A) ESMから最新の状態XMLを取得
                    current_state_xml = esm.get_state_as_xml_prompt()
                    # (B) 最新の状態でシステムプロンプトを構築
                    house = (payload.get("house") if isinstance(payload, dict) else "") or ""
                    room = (payload.get("room") if isinstance(payload, dict) else "") or ""
                    system_prompt_content = safe_format_prompt(
                        st.session_state.system_prompt_template,
                        current_state_xml=current_state_xml,
                        house=house,
                        room=room,
                    )
                    system_message = {"role": "system", "content": system_prompt_content}

                    # (C) APIに渡すメッセージリストを作成
                    messages_for_api = [system_message] + context

                    # (D) LLM API 呼び出し
                    if not st.session_state.get("task_timer_started_at"):
                        st.session_state["task_timer_started_at"] = datetime.now(timezone.utc).isoformat()
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",  # または "gpt-4-turbo"
                        messages=messages_for_api,
                    )
                    reply = response.choices[0].message.content.strip()

                    # (E) 応答をコンテキストに追加
                    spoken_response = extract_xml_tag(reply, "SpokenResponse")
                    if not spoken_response:
                        spoken_response = strip_tags(reply) or "(...)"

                    _append_context_message(
                        context,
                        {
                            "role": "assistant",
                            "content": spoken_response,
                            "full_reply": reply,
                        },
                    )
                    st.session_state.turn_count += 1

                    # (F) [フェーズ1] Goalが設定されたかパース
                    goal_def_str = extract_xml_tag(reply, "TaskGoalDefinition")
                    if (
                        goal_def_str
                        and "Goal:" in goal_def_str
                        and not st.session_state.goal_set
                    ):
                        if esm.set_task_goal_from_llm(goal_def_str):
                            st.session_state.goal_set = True
                            st.success("タスク目標を設定しました！")
                        else:
                            st.error("LLMが生成したタスク目標のパースに失敗しました。")

                    # (G) [フェーズ2] 行動計画が生成されたかパース
                    plan_str = extract_xml_tag(reply, "FunctionSequence")
                    if plan_str:
                        # [変更点] 介入時に古い計画がクリアされているため、extendでOK
                        actions = parse_function_sequence(plan_str)
                        if actions:
                            st.session_state.action_plan_queue.extend(actions)
                            st.info(f"{len(actions)}ステップの計画を受信しました。")

                    # (H) 画面を再描画
                    st.rerun()

    if st.session_state.get("force_end"):
        should_stop = True
        end_message = "ユーザーが会話を終了しました。"

    with tab_state:
        st.markdown("#### 現在の状態")
        st.caption(
            "ExternalStateManager (ESM) が保持している状態です。ロボットの行動に応じて更新されます。"
        )

        # --- 1. ロボットの状態 ---
        st.markdown("##### 👀 ロボットの様子")
        col1, col2 = st.columns(2)

        # esm.py のキーに合わせて指定
        robot_stat = current_state.get("robot_status", {})
        location = robot_stat.get("location", "不明")
        holding = robot_stat.get("holding", "なし")

        # 'living_room' -> 'Living Room' のように整形して表示
        col1.metric("現在地", location.replace("_", " ").title())
        col2.metric("掴んでいる物", str(holding) if holding else "なし")

        st.divider()

        # --- 2. 環境の状態 ---
        st.markdown("##### 🏠 環境（場所ごとのアイテム）")
        environment_state = current_state.get("environment", {})

        # 場所が多いため2列に分けて表示
        env_cols = st.columns(2)

        # 辞書のキー（場所）を半分に分ける
        locations = list(environment_state.keys())
        mid_point = (len(locations) + 1) // 2
        locations_col1 = locations[:mid_point]
        locations_col2 = locations[mid_point:]

        # 左側の列
        with env_cols[0]:
            for loc in locations_col1:
                items = environment_state.get(loc, [])
                # 'kitchen_shelf' -> 'Kitchen Shelf'
                loc_label = loc.replace("_", " ").title()

                with st.expander(f"{loc_label} ({len(items)}個)"):
                    if items:
                        st.multiselect(
                            f"（{loc_label}にある物）",
                            items,
                            default=items,
                            disabled=True,
                            label_visibility="collapsed",  # ラベルを非表示に
                        )
                    else:
                        st.info("（何もありません）")

        # 右側の列
        with env_cols[1]:
            for loc in locations_col2:
                items = environment_state.get(loc, [])
                loc_label = loc.replace("_", " ").title()

                with st.expander(f"{loc_label} ({len(items)}個)"):
                    if items:
                        st.multiselect(
                            f"（{loc_label}にある物）",
                            items,
                            default=items,
                            disabled=True,
                            label_visibility="collapsed",
                        )
                    else:
                        st.info("（何もありません）")

        # --- 3. タスク目標 (ついでに表示) ---
        st.divider()
        st.markdown("##### 🎯 現在のタスク目標")
        task_goal = current_state.get("task_goal", {})
        target_loc = task_goal.get("target_location", "未設定")
        items_needed = task_goal.get("items_needed", {})

        col_t1, col_t2 = st.columns(2)
        col_t1.metric("目標地点", str(target_loc).title() if target_loc else "未設定")

        if items_needed:
            # 辞書 { 'itemA': 2, 'itemB': 1 } をリスト表示
            item_list = [f"{item} (x{count})" for item, count in items_needed.items()]
            col_t2.markdown("**必要なアイテム:**")
            col_t2.dataframe(
                item_list,
                use_container_width=True,
                hide_index=True,
                column_config={"value": "アイテム (個数)"},
            )
        else:
            col_t2.metric("必要なアイテム", "なし")

        # --- 元のJSONはデバッグ用に折りたたんで残す ---
        with st.expander("詳細な状態（JSON）"):
            st.json(current_state)

    # 7. 評価フォームの表示（should_stop判定ロジックは変更済み）  
    end_message = ""
    if st.session_state.get("force_end"):
        should_stop = True
        end_message = "ユーザーが会話を終了しました。"
    else:
        pass

    if should_stop:
        if st.session_state.active == True:
            st.success(end_message)
            submitted = render_standard_evaluation_form(
                prompt_group=PROMPT_GROUP,
            )

            if submitted:
                st.session_state.active = False
                st.session_state["experiment_followup_prompt"] = True
                st.session_state.pop("experiment_followup_choice", None)

    with st.container(border=True):
        st.markdown("#### ⚙️操作パネル")
        cols1 = st.columns([2, 1])
        with cols1[0]:
            st.markdown("🤔ロボットが行動しようとしているのに、赤い「実行」ボタンが出てこない場合→")
        with cols1[1]:
            if st.button("▶️実行を始める", key="manual_request_next_plan"):
                next_plan_request = "正しい形式で番号付き行動計画リストも出力して"
                _append_context_message(
                    context,
                    {"role": "user", "content": next_plan_request},
                )
                st.chat_message("user").write(next_plan_request)
                st.session_state.trigger_llm_call = True
                st.rerun()
        cols2 = st.columns([2, 1])
        with cols2[0]:
            st.markdown("⚠️上のボタンを何度押しても上手くいかない場合→")
        with cols2[1]:
            if st.button("🗃️会話履歴を保存", key="reset_conv"):
                save_conversation_history_to_firestore(
                    "保存ボタンが押されました",
                    metadata={
                        "page": "smalltalk",
                        "event": "manual_save_button",
                    },
                    collection_override="conversation_saves",
                    prompt_group=PROMPT_GROUP,
                )
                st.toast("会話履歴をFirestoreに保存しました。ページを再読み込みしてください。")         
        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown("🎉ロボットとの会話を終了したい場合→")
        with cols[1]:
            if st.button("✅タスク完了！", key="force_end_button"):
                if not st.session_state.get("task_duration_recorded"):
                    started_at_raw = st.session_state.get("task_timer_started_at")
                    if started_at_raw:
                        try:
                            started_at = datetime.fromisoformat(started_at_raw)
                        except ValueError:
                            started_at = None
                        if started_at:
                            ended_at = datetime.now(timezone.utc)
                            duration_seconds = (ended_at - started_at).total_seconds()
                            record_task_duration(
                                prompt_group=PROMPT_GROUP,
                                started_at=started_at,
                                ended_at=ended_at,
                                duration_seconds=duration_seconds,
                            )
                            st.session_state["task_duration_recorded"] = True
                st.session_state.force_end = True
                st.rerun()
    if st.session_state.get("experiment_followup_prompt"):
        if NEXT_PAGE:
            if st.button("次の実験へ→", key="followup_no", type="primary"):
                st.session_state["experiment_followup_prompt"] = False
                st.session_state.pop("experiment_followup_choice", None)
                _reset_conversation_state(system_prompt)
                st.switch_page(NEXT_PAGE)
        else:
            st.info("お疲れさまでした。これで全ての実験が終了です。")
            st.balloons()
        # if st.button("🙆‍♂️はい → 実験終了", key="followup_yes", type="primary"):
        #     st.session_state["experiment_followup_prompt"] = False
        #     st.session_state.pop("experiment_followup_choice", None)
        #     st.success("実験お疲れ様でした！ご協力ありがとうございました。")

app()
