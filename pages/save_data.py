import json
import os
import re

import streamlit as st
from pages.consent import require_consent
from dotenv import load_dotenv

from api import client, build_bootstrap_user_message, CREATING_DATA_SYSTEM_PROMPT
from jsonl import (
    remove_last_jsonl_entry,
    save_conversation_history_to_firestore,
    save_jsonl_entry,
    show_jsonl_block,
)
from move_functions import move_to, pick_object, place_object_next_to, place_object_on
from run_and_show import run_plan_and_show, show_spoken_response, show_function_sequence, show_information
from tasks.ui import render_random_room_task, reset_random_room_task

load_dotenv()


def accumulate_information(reply: str) -> str:
    info_match = re.search(r"<Information>([\s\S]*?)</Information>", reply, re.IGNORECASE)
    if not info_match:
        return reply
    if "information_items" not in st.session_state:
        st.session_state.information_items = []
    items = re.findall(r"<li>(.*?)</li>", info_match.group(1))
    st.session_state.information_items.extend(items)
    aggregated = "<Information>\n" + "\n".join(f"  <li>{item}</li>" for item in st.session_state.information_items) + "\n</Information>"
    return re.sub(r"<Information>[\s\S]*?</Information>", aggregated, reply)


def app():
    # require_consent()
    # st.title("LLMATCH Criticデモアプリ")
    
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


    image_root = "images"
    house_dirs = [d for d in os.listdir(image_root) if os.path.isdir(os.path.join(image_root, d))]
    default_label = "(default)"
    options = [default_label] + house_dirs
    current_house = st.session_state.get("selected_house", "")
    current_label = current_house if current_house else default_label
    selected_label = st.selectbox(
        "家",
        options,
        index=options.index(current_label) if current_label in options else 0,
    )
    st.session_state["selected_house"] = "" if selected_label == default_label else selected_label

    image_dir = image_root
    subdirs = []
    if st.session_state["selected_house"]:
        image_dir = os.path.join(image_dir, st.session_state["selected_house"])
        subdirs = [d for d in os.listdir(image_dir) if os.path.isdir(os.path.join(image_dir, d))]
    sub_default = "(default)"
    if subdirs:
        current_sub = st.session_state.get("selected_subfolder", "")
        current_sub_label = current_sub if current_sub else sub_default
        sub_options = [sub_default] + subdirs
        sub_label = st.selectbox(
            "部屋",
            sub_options,
            index=sub_options.index(current_sub_label) if current_sub_label in sub_options else 0,
        )
        st.session_state["selected_subfolder"] = "" if sub_label == sub_default else sub_label
        if st.session_state["selected_subfolder"]:
            image_dir = os.path.join(image_dir, st.session_state["selected_subfolder"])
    else:
        st.session_state["selected_subfolder"] = ""

    selected_room = st.session_state.get("selected_subfolder", "")
    render_random_room_task(selected_room, state_prefix="save_data")

    if os.path.isdir(image_dir):
        image_files = [
            f
            for f in os.listdir(image_dir)
            if os.path.isfile(os.path.join(image_dir, f))
            and f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
        ]
        if image_files:
            selected_imgs = st.multiselect("表示する画像", image_files)
            selected_paths = [os.path.join(image_dir, img) for img in selected_imgs]
            st.session_state["selected_image_paths"] = selected_paths
            for path, img in zip(selected_paths, selected_imgs):
                st.image(path, caption=img)
        else:
            st.session_state["selected_image_paths"] = []

    # 1) セッションにコンテキストを初期化（systemだけ先に入れて保持）
    if "context" not in st.session_state:
        st.session_state["context"] = [
            {"role": "system", "content": CREATING_DATA_SYSTEM_PROMPT},
        ]

    if "active" not in st.session_state:
        st.session_state.active = True
    if "conv_log" not in st.session_state:
        st.session_state.conv_log = {
            "label": "",
            "clarifying_steps": []
        }

    if "chat_input_history" not in st.session_state:
        st.session_state["chat_input_history"] = []

    if "information_items" not in st.session_state:
        st.session_state.information_items = []

    context = st.session_state["context"]

    # 2) フォーム：ここで送信したら即時に最初の応答まで取得して表示
    with st.form(key="instruction_form"):
        st.subheader("ロボットへの指示")
        instruction = st.text_input("ロボットへの指示")
        submit_btn = st.form_submit_button("実行")

    if submit_btn:
        if not instruction.strip():
            st.warning("指示が空です。内容を入力してください。")
        else:
            # フォーム送信のタイミングでユーザー指示を表示
            st.success(f"ロボットへの指示がセットされました：**{instruction}**")
            st.session_state["chat_input_history"] = []
            context.append({"role": "user", "content": instruction})

            selected_paths = st.session_state.get("selected_image_paths", [])
            if selected_paths:
                context.append(
                    build_bootstrap_user_message(
                        text="Here are the selected images. Use them for scene understanding and disambiguation.",
                        local_image_paths=selected_paths,
                    )
                )

            # 2) 最初のアシスタント応答を取得（画像を添えた状態で）
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state["context"]
            )
            reply = (response.choices[0].message.content).strip()
            reply = accumulate_information(reply)
            st.session_state["context"].append({"role": "assistant", "content": reply})
            save_jsonl_entry("insufficient")


    # 3) 追加の自由入力（会話継続用）
    user_input = st.chat_input("入力してください", key="save_data_chat_input")
    if user_input:
        context.append({"role": "user", "content": user_input})
        st.session_state["chat_input_history"].append(user_input)
        selected_paths = st.session_state.get("selected_image_paths", [])
        if selected_paths:
            context.append(
                build_bootstrap_user_message(
                    text="Here are the selected images. Use them for scene understanding and disambiguation.",
                    local_image_paths=selected_paths,
                )
            )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=context
        )
        reply = response.choices[0].message.content.strip()
        reply = accumulate_information(reply)
        print("Assistant:", reply)
        context.append({"role": "assistant", "content": reply})
        print("context: ", context)
        save_jsonl_entry("insufficient")  # ←この行を追加

    # 4) 画面下部に履歴を全表示（systemは省く）
    last_assistant_idx = max((i for i, m in enumerate(context) if m["role"] == "assistant"), default=None)

    for i, msg in enumerate(context):
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                if i == last_assistant_idx and "<FunctionSequence>" in msg["content"]:
                    run_plan_and_show(msg["content"])
                show_function_sequence(msg["content"])
                show_spoken_response(msg["content"])
                show_information(msg["content"])
        # 最後のアシスタント直後にボタンを出す（計画があるときのみ）
        if i == last_assistant_idx and "<FunctionSequence>" in msg["content"]:
            st.write("この計画はロボットが実行するのに十分ですか？")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("十分", key=f"enough_{i}"):
                    remove_last_jsonl_entry()
                    save_jsonl_entry("sufficient")
                    st.session_state.active = False
                    st.rerun()
            with col2:
                if st.button("不十分", key=f"not_enough_{i}"):
                    clarify_prompt = {
                        "role": "system",
                        "content": "The previous plan was insufficient. Ask a clarifying question to the user to improve it."
                    }
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=context + [clarify_prompt]
                    )
                    question = response.choices[0].message.content.strip()
                    context.append({"role": "assistant", "content": question})
                    save_jsonl_entry("insufficient")
                    st.rerun()
            if st.session_state.active == False:
                show_jsonl_block()
                st.warning("会話を終了しました。ありがとうございました！")
                if st.button("⚠️会話をリセット", key="reset_conv"):
                    save_conversation_history_to_firestore(
                        "会話をリセットしました",
                        metadata={"page": "save_data"},
                        collection_override="conversation_resets",
                    )
                    st.session_state.context = [{"role": "system", "content": CREATING_DATA_SYSTEM_PROMPT}]
                    st.session_state.active = True
                    st.session_state.conv_log = {
                        "label": "",
                        "clarifying_steps": []
                    }
                    st.session_state.saved_jsonl = []
                    st.session_state.information_items = []
                    st.session_state["chat_input_history"] = []
                    reset_random_room_task("save_data")
                    st.rerun()
                st.stop()

app()
