import os
from pathlib import Path
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv

from image_task_sets import (
    build_task_set_choices,

    delete_image_task_set,
    load_image_task_sets,
    upsert_image_task_set,
)

load_dotenv()

IMAGE_ROOT = Path("images")
NEW_SET_LABEL = "(新規作成)"
DEFAULT_LABEL = "(default)"
RESET_TRIGGER_KEY = "reset_task_form_trigger"


def _ensure_form_state() -> None:
    defaults: Dict[str, str | List[str]] = {
        "task_description": "",
        "selected_house": "",
        "selected_subfolder": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("selected_image_paths", [])
    st.session_state.setdefault("current_task_set_choice", NEW_SET_LABEL)
    st.session_state.setdefault(RESET_TRIGGER_KEY, False)


def _reset_form_state() -> None:
    st.session_state.update(
        {
            "task_description": "",
            "selected_house": "",
            "selected_subfolder": "",
            "selected_image_paths": [],
            "current_task_set_choice": NEW_SET_LABEL,
            RESET_TRIGGER_KEY: False,
        }
    )


def _populate_form_from_set(name: str, payload: Dict[str, object]) -> None:
    tasks = payload.get("tasks") if isinstance(payload, dict) else []
    task_lines: List[str] = []
    if isinstance(tasks, list):
        task_lines = [str(t) for t in tasks if str(t).strip()]
    elif isinstance(tasks, str):
        task_lines = [line.strip() for line in tasks.splitlines() if line.strip()]
    elif isinstance(payload, dict):
        raw_text = payload.get("task_text")
        if isinstance(raw_text, str):
            task_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    st.session_state.update(
        {
            "task_description": "\n".join(task_lines),
            "selected_house": str(payload.get("house", "")) if isinstance(payload, dict) else "",
            "selected_subfolder": str(payload.get("room", "")) if isinstance(payload, dict) else "",
            "selected_image_paths": [
                str(path) for path in payload.get("images", [])
            ]
            if isinstance(payload, dict)
            else [],
            "current_task_set_choice": name,
            RESET_TRIGGER_KEY: False,
        }
    )



def app():
    # st.title("LLMATCH Criticデモアプリ")
    st.subheader("写真とタスクの選定・保存")

    st.sidebar.subheader("行動計画で使用される関数")
    st.sidebar.markdown(
        """
        - **move_to(room_name:str)**
        指定した部屋へロボットを移動します。

        - **pick_object(object:str)**
        指定した物体をつかみます。

        - **place_object_next_to(object:str, target:str)**
        指定した物体をターゲットの横に置きます。

        - **place_object_on(object:str, target:str)**
        指定した物体をターゲットの上に置きます。

        - **place_object_in(object:str, target:str)**
        指定した物体をターゲットの中に入れます。

        - **detect_object(object:str)**
        指定した物体を検出します。

        - **search_about(object:str)**
        指定した物体に関する情報を検索します。

        - **push(object:str)**
        指定した物体を押します。

        - **say(text:str)**
        指定したテキストを発話します。
        """
    )

    _ensure_form_state()

    if st.session_state.pop(RESET_TRIGGER_KEY, False):
        _reset_form_state()

    task_sets = load_image_task_sets()
    choice_pairs = build_task_set_choices(task_sets)
    labels = [label for label, _ in choice_pairs]
    label_to_key = {label: key for label, key in choice_pairs}

    selection_options = [NEW_SET_LABEL] + labels

    current_key = st.session_state.get("current_task_set_choice", NEW_SET_LABEL)
    valid_keys = {key for _, key in choice_pairs}
    if current_key not in valid_keys and current_key != NEW_SET_LABEL:
        if current_key in label_to_key:
            current_key = label_to_key[current_key]
        else:
            current_key = NEW_SET_LABEL
        st.session_state["current_task_set_choice"] = current_key
    if not labels:
        default_label = NEW_SET_LABEL
    elif current_key != NEW_SET_LABEL:
        default_label = next(
            (label for label, key in choice_pairs if key == current_key),
            NEW_SET_LABEL,
        )
    else:
        default_label = NEW_SET_LABEL

    selected_label = st.selectbox(
        "保存済みのタスク",
        selection_options,
        index=selection_options.index(default_label) if default_label in selection_options else 0,
    )

    selected_key = label_to_key.get(selected_label, NEW_SET_LABEL)

    if selected_key != current_key:
        if selected_key == NEW_SET_LABEL:
            _reset_form_state()
        else:
            payload = task_sets.get(selected_key, {})
            _populate_form_from_set(selected_key, payload)

    # --- タスクセット名とタスク内容 ---
    st.text_area("タスク（1行につき1つの指示を入力してください）", height=120, key="task_description")

    # --- 画像の選択 ---
    house_dirs = sorted([d for d in os.listdir(IMAGE_ROOT) if (IMAGE_ROOT / d).is_dir()])
    house_options = [DEFAULT_LABEL] + house_dirs
    current_house = st.session_state.get("selected_house", "")
    current_house_label = current_house if current_house else DEFAULT_LABEL
    house_label = st.selectbox(
        "家",
        house_options,
        index=house_options.index(current_house_label)
        if current_house_label in house_options
        else 0,
    )
    st.session_state["selected_house"] = "" if house_label == DEFAULT_LABEL else house_label

    image_dir = IMAGE_ROOT
    subdirs: List[str] = []
    if st.session_state["selected_house"]:
        image_dir = image_dir / st.session_state["selected_house"]
        subdirs = sorted([d for d in os.listdir(image_dir) if (image_dir / d).is_dir()])

    if subdirs:
        current_sub = st.session_state.get("selected_subfolder", "")
        current_sub_label = current_sub if current_sub else DEFAULT_LABEL
        sub_options = [DEFAULT_LABEL] + subdirs
        sub_label = st.selectbox(
            "部屋",
            sub_options,
            index=sub_options.index(current_sub_label)
            if current_sub_label in sub_options
            else 0,
        )
        st.session_state["selected_subfolder"] = "" if sub_label == DEFAULT_LABEL else sub_label
        if st.session_state["selected_subfolder"]:
            image_dir = image_dir / st.session_state["selected_subfolder"]
    else:
        st.session_state["selected_subfolder"] = ""

    selected_paths: List[str] = st.session_state.get("selected_image_paths", [])
    image_files: List[str] = []
    if image_dir.is_dir():
        image_files = sorted(
            [
                f
                for f in os.listdir(image_dir)
                if (image_dir / f).is_file()
                and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
            ]
        )

    image_dir_str = str(image_dir)
    default_images = [
        os.path.basename(path)
        for path in selected_paths
        if os.path.dirname(path) == image_dir_str
    ]

    selected_imgs = st.multiselect(
        "表示する画像",
        image_files,
        default=default_images,
    )
    st.session_state["selected_image_paths"] = [
        str(image_dir / img) for img in selected_imgs
    ]

    st.markdown("### 選択中の画像")
    if st.session_state["selected_image_paths"]:
        for path in st.session_state["selected_image_paths"]:
            if os.path.exists(path):
                st.image(path, caption=os.path.basename(path))
            else:
                st.warning(f"画像ファイルが見つかりません: {path}")
    else:
        st.info("画像を1枚以上選択してください。")

    # --- 保存処理 ---
    if st.button("タスクを保存", type="primary"):
        tasks_text = st.session_state.get("task_description", "")
        image_paths = st.session_state.get("selected_image_paths", [])

        errors = []
        if not image_paths:
            errors.append("画像を1枚以上選択してください。")
        task_lines = [line.strip() for line in tasks_text.splitlines() if line.strip()]
        if not task_lines:
            errors.append("タスクを1行以上入力してください。")

        if errors:
            for err in errors:
                st.error(err)
        else:
            name = "\n".join(task_lines)
            payload = {
                "house": st.session_state.get("selected_house", ""),
                "room": st.session_state.get("selected_subfolder", ""),
                "images": image_paths,
                "tasks": task_lines,
                "task_text": "\n".join(task_lines),
            }
            upsert_image_task_set(name, payload)
            st.session_state["current_task_set_choice"] = name
            st.success("タスクを保存しました。")

    if selected_key != NEW_SET_LABEL and st.button("選択中のタスクを削除", type="secondary"):
        if selected_key in task_sets:
            delete_image_task_set(selected_key)
            st.success("選択中のタスクを削除しました。")
        else:
            st.warning("削除対象のタスクが見つかりませんでした。")
        st.session_state[RESET_TRIGGER_KEY] = True
        st.rerun()

    st.markdown("### 保存済みタスク一覧")
    refreshed_sets = load_image_task_sets()
    if not refreshed_sets:
        st.info("保存済みのタスクはまだありません。")
    else:
        refreshed_choices = build_task_set_choices(refreshed_sets)
        for label, key in refreshed_choices:
            data = refreshed_sets.get(key, {})
            tasks = data.get("tasks", []) if isinstance(data, dict) else []
            st.markdown(
                f"- **{label}**: {', '.join(tasks) if tasks else 'タスク未登録'}"
            )

app()
