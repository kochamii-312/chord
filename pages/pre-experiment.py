import streamlit as st
from pages.consent import require_consent
import json
import os
from difflib import SequenceMatcher
from pathlib import Path
from dotenv import load_dotenv

from utils.api import client, SYSTEM_PROMPT, build_bootstrap_user_message
from archive.jsonl import (
    predict_with_model,
    save_conversation_history_to_firestore,
    save_pre_experiment_result,
)
from utils.run_and_show import (
    run_plan_and_show,
    show_spoken_response,
    show_function_sequence,
)
from utils.strips import extract_between, strip_tags
from tasks.ui import render_random_room_task, reset_random_room_task

load_dotenv()

@st.cache_data
def load_ground_truth_map():
    """Load instruction to function_sequence mapping from dataset."""
    dataset_path = Path(__file__).resolve().parents[1] / "json" / "function_sequence_truth.jsonl"
    mapping = {}
    if dataset_path.exists():
        with dataset_path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                fs = obj.get("function_sequence")
                inst = obj.get("instruction")
                if fs and inst and inst not in mapping:
                    mapping[inst] = fs
    return mapping

def show_provisional_output(reply: str):
    show_function_sequence(reply)
    show_spoken_response(reply)
    run_plan_and_show(reply)

def finalize_and_render_plan(label: str):
    """会話終了時に行動計画をまとめて画面表示"""
    # final_answer の決定
    last_assistant = next(
        (m for m in reversed(st.session_state.context) if m['role'] == 'assistant'),
        None,
    )
    final_answer = (
        extract_between('FinalAnswer', last_assistant['content'])
        if last_assistant
        else None
    )
    if not final_answer and last_assistant:
        final_answer = strip_tags(last_assistant['content'])

    st.session_state.conv_log['final_answer'] = final_answer or ''
    st.session_state.conv_log['label'] = (
        'sufficient' if label == 'sufficient' else 'insufficient'
    )
    generated_fs = extract_between('FunctionSequence', last_assistant['content']) if last_assistant else ''
    
    # question_label が None のステップは継続が無ければ insufficient で埋める
    for s in st.session_state.conv_log['clarifying_steps']:
        if s['question_label'] is None:
            s['question_label'] = 'insufficient'

    st.subheader('会話サマリ（JSON）')
    st.code(
        json.dumps(st.session_state.conv_log, ensure_ascii=False, indent=2),
        language='json',
    )

    gt_fs = st.session_state.get('correct_function_sequence', '')
    if gt_fs and generated_fs:
        sim = SequenceMatcher(None, generated_fs, gt_fs).ratio()
        st.subheader('Function sequence 類似度')
        st.write(f"{sim:.2f}")

def app():
    # require_consent()
    # st.title("LLMATCH Criticデモアプリ")
    st.subheader("プレ実験")
    st.write("目的：GPT with Criticの学習の効果を図る。")
    st.write("定量的評価：人間が作った行動計画の正解と、対話によって最終的に生成されたロボットの行動計画を比較し、どれくらい一致するかを検証する。")
    st.write("定性的評価：対話によって最終的に生成されたロボットの行動計画が実行可能かを評価する。")

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

    system_prompt = SYSTEM_PROMPT

    model_files = sorted(
        f for f in os.listdir("models") if f.endswith(".joblib")
    )
    if model_files:
        latest_model = max(
            model_files,
            key=lambda f: os.path.getmtime(os.path.join("models", f)),
        )
        stored_model = st.session_state.get("model_path")
        current_model = os.path.basename(stored_model) if stored_model else None
        if current_model not in model_files:
            current_model = latest_model
        selected_model = st.selectbox(
            "評価モデル",
            model_files,
            index=model_files.index(current_model),
        )
        st.session_state["model_path"] = os.path.join("models", selected_model)

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
    render_random_room_task(selected_room, state_prefix="pre_experiment")

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
    if (
        "context" not in st.session_state
        or st.session_state.get("system_prompt") != system_prompt
    ):
        st.session_state["context"] = [{"role": "system", "content": system_prompt}]
        st.session_state["system_prompt"] = system_prompt
        st.session_state.conv_log = {
            "final_answer": "",
            "label": "",
            "clarifying_steps": []
        }
        st.session_state["chat_input_history"] = []
    if "active" not in st.session_state:
        st.session_state.active = True
    if "chat_input_history" not in st.session_state:
        st.session_state["chat_input_history"] = []

    gt_map = load_ground_truth_map()
    inst_options = ["(未選択)"] + list(gt_map.keys())
    selected_inst = st.selectbox(
        "評価用命令を選択",
        inst_options,
        index=inst_options.index(st.session_state.get("selected_instruction", "(未選択)"))
        if st.session_state.get("selected_instruction", "(未選択)") in inst_options
        else 0,
    )
    if selected_inst != "(未選択)":
        st.session_state["selected_instruction"] = selected_inst
        st.session_state["correct_function_sequence"] = gt_map[selected_inst]
    if st.button("命令を送信") and selected_inst != "(未選択)":
        st.session_state["pending_user_input"] = selected_inst

    context = st.session_state["context"]

    message = st.chat_message("assistant")
    message.write("こんにちは、私は家庭用ロボットです！あなたの指示に従って行動します。")
    input_box = st.chat_input("ロボットへの回答を入力してください", key="pre-experiment_chat_input")
    if input_box:
        st.session_state["chat_input_history"].append(input_box)
    user_input = st.session_state.pop("pending_user_input", None) or input_box
    
    if user_input:
        context.append({"role": "user", "content": user_input})
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
        print("Assistant:", reply)
        context.append({"role": "assistant", "content": reply})
        print("context: ", context)
        label = predict_with_model()
        if label == "sufficient":
            st.success("モデルがsufficientを出力したため終了します。")
            finalize_and_render_plan(label)
            if st.session_state.active == False:
                st.warning("会話を終了しました。ありがとうございました！")
                if st.button("⚠️会話をリセット", key="reset_conv"):
                    save_conversation_history_to_firestore(
                        "会話をリセットしました",
                        metadata={"page": "pre_experiment"},
                        collection_override="pre_experiment_results",
                    )
                    st.session_state.context = [{"role": "system", "content": SYSTEM_PROMPT}]
                    st.session_state.active = True
                    st.session_state.conv_log = {
                        "label": "",
                        "clarifying_steps": []
                    }
                    st.session_state.saved_jsonl = []
                    reset_random_room_task("pre_experiment")
                    st.rerun()
                st.stop()

    last_assistant_idx = max((i for i, m in enumerate(context) if m["role"] == "assistant"), default=None)
        
    # 画面下部に履歴を全表示（systemは省く）

    for i, msg in enumerate(context):
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
        
        # if i == last_assistant_idx:
        #     show_provisional_output(msg["content"])

        # if i == last_assistant_idx: #and "<FinalOutput>" in msg["content"]:
            
    if st.button("⚠️会話をリセット", key="reset_conv"):
        save_conversation_history_to_firestore(
            "会話をリセットしました",
            metadata={"page": "pre_experiment"},
            collection_override="pre_experiment_results",
        )
        # セッション情報を初期化
        st.session_state.context = [{"role": "system", "content": system_prompt}]
        st.session_state.active = True
        st.session_state.conv_log = {
            "label": "",
            "clarifying_steps": []
        }
        st.session_state.saved_jsonl = []
        st.session_state["chat_input_history"] = []
        reset_random_room_task("pre_experiment")
        st.rerun()

app()
