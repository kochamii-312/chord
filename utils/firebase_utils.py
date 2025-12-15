import json
import os
from typing import Any, Dict, Optional

import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st


def _initialize_firebase_app(cred: credentials.Base) -> None:
    """Firebase Admin SDKを初期化する。既に初期化済みの場合は何もしない。"""

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)


def _get_credentials_from_streamlit() -> Optional[credentials.Certificate]:
    """Streamlit secretsからサービスアカウント資格情報を取得する。"""

    try:
        sa_info = dict(st.secrets["gcp_service_account"])
    except (AttributeError, KeyError, RuntimeError):
        return None
    except Exception:
        # streamlit側で予期せぬ例外が出た場合は、他の認証手段にフォールバックする
        return None

    private_key = sa_info.get("private_key")
    if isinstance(private_key, str) and "\\n" in private_key:
        sa_info["private_key"] = private_key.replace("\\n", "\n")

    return credentials.Certificate(sa_info)


def _load_certificate_from_source(source: str) -> credentials.Certificate:
    """Load Firebase credentials from a file path or JSON string."""

    source = source.strip()

    if source.startswith("{"):
        try:
            info = json.loads(source)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON credential string") from exc

        private_key = info.get("private_key")
        if isinstance(private_key, str):
            info["private_key"] = private_key.replace("\\n", "\n")

        return credentials.Certificate(info)

    if os.path.exists(source):
        return credentials.Certificate(source)

    raise FileNotFoundError(f"Credentials file not found: {source}")


def _get_default_credentials() -> credentials.Base:
    """利用可能な認証情報から優先順位に沿って資格情報を取得する。"""

    streamlit_credentials = _get_credentials_from_streamlit()
    if streamlit_credentials is not None:
        return streamlit_credentials

    credentials_source = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_source:
        try:
            return _load_certificate_from_source(credentials_source)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Credentials file not found: {credentials_source}"
            ) from exc
        except ValueError as exc:
            raise ValueError(
                "Invalid JSON credential string provided via GOOGLE_APPLICATION_CREDENTIALS"
            ) from exc

    try:
        return credentials.ApplicationDefault()
    except Exception as exc:
        raise RuntimeError(
            "No valid Firestore credentials found. Please configure Streamlit "
            "secrets, set GOOGLE_APPLICATION_CREDENTIALS, or provide a "
            "credentials file."
        ) from exc


def _get_db_from_secrets() -> firestore.Client:
    """Streamlit secretsからGCPサービスアカウント情報を取得してFirestore接続"""

    cred = _get_default_credentials()
    _initialize_firebase_app(cred)
    return firestore.client()


def _get_db_from_credentials_source(credentials_source: str) -> firestore.Client:
    """ファイルパスまたはJSON文字列で指定されたサービスアカウント情報からFirestoreへ接続"""

    cred = _load_certificate_from_source(credentials_source)
    _initialize_firebase_app(cred)
    return firestore.client()


def save_document(
    collection: str,
    data: Dict[str, Any],
    credentials_source: Optional[str] = None,
) -> None:
    """Firestoreコレクションにドキュメントを保存"""

    if credentials_source:
        db = _get_db_from_credentials_source(credentials_source)
    else:
        db = _get_db_from_secrets()
    db.collection(collection).add(data)
