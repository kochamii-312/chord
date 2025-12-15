"""Streamlit helpers for obtaining participant consent before running the app."""

from __future__ import annotations

import os
from datetime import date, datetime, timezone

import streamlit as st

from utils.firebase_utils import save_document

from dotenv import load_dotenv

load_dotenv()

ROLE_PARTICIPANT = "被験者"
ROLE_DEBUG = "デバッグ"

SIDEBAR_HIDE_STYLE = """
    <style>
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="stSidebarNav"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
    </style>
"""


CONSENT_TEXT = """
### 「対話型LLMによる家庭内ロボット行動計画とタスク達成率：人-AIインタラクションの効果」に対するご協力のお願い

#### 1　目的
本研究の目的は、人とAIのコミュニケーションの仕方（丁寧さや順序・説明の明確さなど）が、家庭用ロボットのタスク達成率に与える影響を明らかにすることです。

そのために、家庭用ロボットに相当するデモアプリを作成しました。参加者はアプリ上で家の用事（例：ものを片付ける、必要なものを探すなど）をロボットに指示します。AI（大規模言語モデル）は、作業に必要な情報が足りていない場合に「何を・どこで・どの順で行うか」を質問し、十分な情報が集まるまで対話を続けます。集めた情報に基づいて、AIは手順（行動計画）を段階的に更新し、タスク完了を目指します。

この一連の流れを通して、コミュニケーションの違いが最終的な達成率にどの程度聞いているかを評価します。

#### 2　協力していただく内容
**対象者**：18歳以上の健常者

**実施方法**：
- 事前のオンライン説明会（約20分）に参加していただきます。
- その後、スマートフォンでWebアプリにアクセスし、指示に沿ってチャットボットと対話していただきます。
- 実験は合計5セッション（実験1の2条件＋実験2の3条件）を行い、各セッションの直後にアンケートに回答していただきます。
- 全体の所要時間は約20〜30分で、必要に応じていつでも休憩できます。

**実験の実施内容**：画面に表示されるタスクに関して、家庭用ロボットに与える指示を入力すると、AIから質問が来ます。これに回答することにより、AIとの会話を通じてAIが自動的に行動計画を作成します。会話終了後、ロボットの行動計画と会話を通した感触の評価に関する簡単なアンケートに回答いただきます。

**記録する内容**：生成AIの出力、チャットのやり取り本文、被験者区別用のニックネーム、アンケート回答

**使用技術**：OpenAI GPT-4o-mini をAPI経由で用います。サーバはGoogle Cloud（Cloud Run／Firestore）を使用します。

**謝礼の有無**：参加に関する謝礼はありません。

#### 3　もたらされるリスク
対話中に長時間の実験・ロボットを想定したチャットボットが思ったように回答を返してこないこと等による戸惑い・疲労を感じる可能性があります。実験中はアプリの画面にて休憩を促しますので、適宜休憩をはさんでください。万が一実験の継続が困難な疲労を感じた場合は速やかに実験を中止します。

また、入力内容に個人情報が含まれると、漏えい時の影響が大きくなります。実名や学籍番号、住所、健康情報などの機微な個人情報は入力しないでください。ニックネームの使用をお願いします。

計測したデータは、仮名加工情報化した形でオープンデータセットとして公開されます。オープンデータセットとしての公開は事前に許諾を得ます。許諾を得られなかった場合は実験参加を取りやめていただきます。またデータの公開後にデータの削除の申し出があった場合は、直ちにデータを非公開にし消去いたします。

#### 4　研究協力に同意しない場合
実験の参加に協力しないことによる不利益は一切発生いたしません。

#### 5　研究協力の同意の撤回
実験の参加を同意された後でも、理由の如何を問わず実験参加を取りやめることができます。
参加を取りやめたことによる不利益は一切発生いたしません。

#### 6　個人情報の保護
実験においては個人毎に計測したデータを記録します。実験終了後は参加者の名前は仮名加工情報化して、保存、解析、およびオープンデータセットとしての公開を行います。データセットの仮名加工情報化に関して、参加者を記号で表すこととし、研究責任者・申請者のみが名前と記号の対応を確認できるものとします。実験に参加していただいた順に A、B、C、とアルファベット順に記号化します。仮名加工情報化の対応表は、紙媒体で保存せず研究責任者・申請者のみがアクセスすることが可能なクラウドフォルダにて管理します。また、学会等での発表資料や学術論文において公表する際に個人名が公表されることはございません。

#### 7　研究結果の公表
実験後、取得したデータは研究室内で保存、解析等されるほか、学会での発表資料や論文で公表されることがあります。実験前に必ず実験者がデータの利用目的を説明し、同意した場合のみ公表の対象となります。なお、データの公表利用に同意しないことによる不利益は一切発生いたしません。

#### 8　研究終了後のデータおよび試料等の取り扱い方針
測定したデータは紙媒体で保存せず、研究責任者・申請者のみがアクセスすることが可能なクラウドフォルダにて管理いたします。処分を希望される際にはサーバおよびコンピュータ上、公開したオープンデータセット上から速やかに削除いたします。オープンデータセットを除くデータの保存期間は、研究発表から10年とします。

#### 9　本研究の費用
本研究に参加する際に対象者が費用を負担することは一切ありません。

#### 10　問い合わせ先
慶應義塾大学理工学部情報工学科 吉田馨
直通電話 070-4286-4557,電子メール kaoru.yoshida@keio.jp

研究内容やデータの取り扱いに関するご質問は、Slack の [@Kaoru Yoshida](https://matsuokenllmcommunity.slack.com/team/U071ML4LY5C) までお問い合わせください。

上記の説明を読み、内容を理解した上で参加に同意する場合は、以下のチェックボックスをオンにしてボタンを押してください。
"""


FIREBASE_CONSENT_COLLECTION_ENV = "FIREBASE_CONSENT_COLLECTION"
DEFAULT_CONSENT_COLLECTION = "consent_signatures"
FIREBASE_CREDENTIALS_ENV = "FIREBASE_CREDENTIALS"
GOOGLE_APPLICATION_CREDENTIALS_ENV = "GOOGLE_APPLICATION_CREDENTIALS"

def get_participant_role() -> str:
    """Return the currently selected participant role."""

    role = st.session_state.get("participant_role", ROLE_PARTICIPANT)
    return role if role in (ROLE_PARTICIPANT, ROLE_DEBUG) else ROLE_PARTICIPANT


def should_hide_sidebar() -> bool:
    """Determine whether the sidebar should be hidden for the current role."""

    return get_participant_role() == ROLE_PARTICIPANT


def configure_page(*, hide_sidebar_for_participant: bool = False, **kwargs) -> None:
    """Configure the page, optionally collapsing the sidebar for participants."""

    if hide_sidebar_for_participant:
        initial_state = "collapsed" if should_hide_sidebar() else "expanded"
        st.set_page_config(initial_sidebar_state=initial_state, **kwargs)
    else:
        st.set_page_config(**kwargs)


def apply_sidebar_hiding() -> None:
    """Inject CSS that hides the sidebar controls."""

    st.markdown(SIDEBAR_HIDE_STYLE, unsafe_allow_html=True)


def _save_consent_record_to_firestore(entry: dict) -> bool:
    """Persist consent data to Firestore."""

    collection = (
        os.getenv(FIREBASE_CONSENT_COLLECTION_ENV, DEFAULT_CONSENT_COLLECTION) or ""
    ).strip()
    if not collection:
        print("[Consent] skipped saving: collection name is not configured")
        return False

    credentials_source = (
        os.getenv(FIREBASE_CREDENTIALS_ENV)
        or os.getenv(GOOGLE_APPLICATION_CREDENTIALS_ENV)
        or None
    )
    # _save_consent_record_to_firestore 内部の try の直前あたりに
    source = "ADC(default)"
    if os.getenv("FIREBASE_CREDENTIALS"):
        source = "FIREBASE_CREDENTIALS(inline JSON)"
    elif os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        p = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        source = f"GOOGLE_APPLICATION_CREDENTIALS(file at {p})"

    print(f"[Consent] using credential source: {source}")

    try:
        save_document(collection, entry, credentials_source)
    except Exception as exc:
        print(f"[Consent] ERROR saving consent record: {exc}")
        return False

    print(f"[Consent] saved consent record to {collection}")
    return True


def _render_consent_form() -> None:
    """Render the consent form and stop execution until the user agrees."""

    st.set_page_config(page_title="研究参加に関する同意", layout="wide")
    st.markdown(CONSENT_TEXT)

    # 利用モード（既存仕様を踏襲）
    role_options = [ROLE_PARTICIPANT, ROLE_DEBUG]
    current_role = get_participant_role()

    st.markdown("---")
    st.markdown("### 協力の同意書")
    st.caption("以下の各項目を確認のうえ、チェックを入れてください。")

    st.write("　私は，「対話型LLMによる家庭内ロボット行動計画とタスク達成率：人-AIインタラクションの効果」について，目的，方法などに関する以下の説明を文書および口頭により受け，内容について十分理解しました。この書面をもって，私がこの研究に参加することを自由意思で決定したことを示すものとします。")

    items = {
        "1": "1.研究目的",
        "2": "2.協力内容",
        "3": "3.リスク",
        "4": "4.調査に同意しない場合でも不利益を受けないこと",
        "5": "5.調査に同意した後，いつでも同意を撤回できること",
        "6": "6.個人情報の保護",
        "7": "7.研究成果の公表",
        "8": "8.研究終了後のデータおよび試料等の取り扱い",
        "9": "9.費用に関する事項",
        "10": "10.問い合わせ先",
    }
    check_keys = [f"consent_item_{k}" for k in items.keys()]

    # すべてチェック ボタン（フォームの外、押下→状態更新→再実行）
    left, right = st.columns([1, 1])
    with left:
        if st.button("すべてチェック", help="1〜10 の全項目にチェックを入れます"):
            for key in check_keys:
                st.session_state[key] = True
            st.success("全項目にチェックを入れました。")
            st.rerun()
    with right:
        # 任意：外すボタン（不要なら削除してOK）
        if st.button("すべて外す", help="チェックをすべて外します"):
            for key in check_keys:
                st.session_state[key] = False
            st.info("すべてのチェックを外しました。")
            st.rerun()

    with st.form("consent_form", clear_on_submit=False):
        selected_role = st.radio(
            "利用モードを選択してください",
            options=role_options,
            index=role_options.index(current_role),
            horizontal=True,
            help="被験者モードではサイドバーを非表示にします。デバッグモードでは常に表示します。",
        )

        for k in items:
            st.session_state.setdefault(f"consent_item_{k}", False)

        checks = {}
        for k, label in items.items():
            key = f"consent_item_{k}"
            # value= を渡さず、セッションステートの値だけに任せる
            checks[k] = st.checkbox(f"{k}. {label}", key=key)

        # 7.1 データ公表可否（単一選択）
        st.markdown("**7.1 データの公表についていずれかを選択してください**")
        data_pub_choice = st.radio(
            "データの公表について",
            ["データの公表に同意する", "データの公表に同意しない"],
            horizontal=True,
            key="data_publication_choice",
        )

        st.divider()

        # 署名欄
        col1, col2 = st.columns(2)
        with col1:
            participant_name = st.text_input("同意者署名（自署/記名）", key="participant_signature_name")
            participant_date = st.date_input("同意者 署名日", value=date.today(), key="participant_signature_date")
        with col2:
            # 研究担当者は固定（編集不可）
            researcher_name = st.text_input(
                "研究担当者署名（自署/記名）",
                value="吉田馨",
                key="researcher_signature_name",
                disabled=True,
                help="研究担当者名は自動入力されます。"
            )
            researcher_date = st.date_input(
                "研究担当者 署名日",
                value=date.today(),
                key="researcher_signature_date",
                disabled=True
            )

        submit = st.form_submit_button("同意して実験に進む", use_container_width=True)

    # バリデーションと状態更新
    if submit:
        # チェック済みの項目を厳密に記録
        checked_items = [k for k in items if st.session_state.get(f"consent_item_{k}", False)]
        missing = [k for k in items if not st.session_state.get(f"consent_item_{k}", False)]

        errors = []
        if missing:
            errors.append("未チェックの項目があります: " + ", ".join(missing))
        if not participant_name.strip():
            errors.append("同意者署名を入力してください。")

        if errors:
            for e in errors:
                st.error(e)
        else:
            consent_entry = {
                "submitted_at": datetime.now(timezone.utc),
                "participant_role": selected_role,
                "consent_items": [
                    {
                        "id": k,
                        "label": items[k],
                        "checked": bool(st.session_state.get(f"consent_item_{k}", False)),
                    }
                    for k in items
                ],
                "checked_item_ids": checked_items,
                "data_publication_choice": data_pub_choice,
                "data_publication_agree": data_pub_choice == "データの公表に同意する",
                "participant_signature": {
                    "name": participant_name.strip(),
                    "date": participant_date.isoformat(),
                },
                "researcher_signature": {
                    "name": researcher_name,
                    "date": researcher_date.isoformat(),
                },
            }

            if not _save_consent_record_to_firestore(consent_entry):
                st.error("同意情報の保存に失敗しました。時間をおいて再度お試しください。")
            else:
                st.session_state["participant_role"] = selected_role
                st.session_state["consent_given"] = True
                st.session_state["consent_items_checked"] = checked_items
                st.session_state["data_publication_agree"] = (
                    data_pub_choice == "データの公表に同意する"
                )
                st.session_state["participant_signature"] = consent_entry["participant_signature"]
                st.session_state["researcher_signature"] = consent_entry["researcher_signature"]
                st.session_state["redirect_to_instruction_page"] = True

                st.success("ご同意ありがとうございます。実験画面に進みます。")
                st.rerun()

    st.stop()


def require_consent(
    *, allow_withdrawal: bool = False, redirect_to_instructions: bool = True
) -> None:
    """Ensure that the participant has given consent before proceeding."""

    if not st.session_state.get("consent_given"):
        _render_consent_form()

    if redirect_to_instructions and st.session_state.get("redirect_to_instruction_page"):
        st.session_state["redirect_to_instruction_page"] = False
        st.switch_page("streamlit_app.py")

    if allow_withdrawal:
        with st.sidebar:
            if st.button("同意を撤回してトップに戻る", type="secondary"):
                st.session_state["consent_given"] = False
                st.session_state.pop("participant_role", None)
                st.rerun()
