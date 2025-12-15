"""Firestoreにシンプルにデータを書き込むためのStreamlitページ。"""

from __future__ import annotations

import json
from typing import Any, Dict

import streamlit as st

from utils.firebase_utils import save_document

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Firestore テスト保存", page_icon="📝")

st.title("Firestore へのシンプルな保存テスト")
st.write(
    "Firestore の接続確認用のページです。"
    "コレクション名と JSON データを入力し、保存ボタンを押してください。"
)

collection = st.text_input("コレクション名", value="test_collection")
raw_json = st.text_area(
    "保存したいJSONデータ",
    value="{\n  \"message\": \"Hello Firestore!\"\n}",
    height=160,
)
credentials_source = st.text_input(
    "認証情報 (任意)",
    value="",
    help=(
        "GOOGLE_APPLICATION_CREDENTIALS などの環境変数を使用する場合は空のままで構いません。"
        "サービスアカウントJSONのパス、またはJSON文字列を直接指定することもできます。"
    ),
)

status_placeholder = st.empty()

if st.button("Firestore に保存", use_container_width=True):
    if not collection.strip():
        status_placeholder.error("コレクション名を入力してください。")
    else:
        try:
            data: Dict[str, Any] = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            status_placeholder.error(f"JSON の形式に誤りがあります: {exc}")
        else:
            try:
                save_document(
                    collection=collection.strip(),
                    data=data,
                    credentials_source=credentials_source.strip() or None,
                )
            except Exception as exc:  # pylint: disable=broad-except
                status_placeholder.error(
                    "Firestore への保存に失敗しました。詳細: " f"{exc}"
                )
            else:
                status_placeholder.success("Firestore への保存に成功しました。")
                st.json(data)
