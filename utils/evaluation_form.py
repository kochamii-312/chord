"""Shared evaluation form utilities for experiment pages."""

from __future__ import annotations

from typing import Dict, Tuple

import streamlit as st

from jsonl import save_experiment_result

SUS_OPTIONS: Tuple[Tuple[str, int], ...] = (
    ("とても当てはまる (5)", 5),
    ("やや当てはまる (4)", 4),
    ("どちらでもない (3)", 3),
    ("あまり当てはまらない (2)", 2),
    ("まったく当てはまらない (1)", 1),
)

SUS_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("sus_q1", "このロボットを頻繁に使用したい"),
    ("sus_q2", "このロボットは必要以上に複雑だと思う"),
    ("sus_q3", "このロボットは使いやすいと感じた"),
    ("sus_q4", "このロボットを使うには専門的なサポートが必要だ"),
    ("sus_q5", "このロボットの様々な機能は統合されていると感じた"),
    ("sus_q6", "このロボットは一貫性が欠けていると思う"),
    ("sus_q7", "大半の人はこのロボットをすぐに使いこなせるようになると思う"),
    ("sus_q8", "このロボットは操作しにくい"),
    ("sus_q9", "このロボットを使いこなせる自信がある"),
    ("sus_q10", "このロボットを使い始める前に知らなければならないことがたくさんあると思う"),
)

NASA_TLX_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    (
        "nasa_mental_demand",
        "あなたは、ロボットと会話をするにあたって、精神的要求（思考，意志決定，計算，記憶，観察，検索，等）がどれくらい要求されましたか？",
    ),
    (
        "nasa_physical_demand",
        "あなたは、ロボットと会話をするにあたって、身体的要求（押す，引く，回す， 操作する等）がどれくらい要求されましたか？",
    ),
    (
        "nasa_temporal_demand",
        "あなたは、ロボットと会話をするにあたって、時間的切迫感（作業や要素作業の頻度や速さ）をどの程度感じましたか？",
    ),
    (
        "nasa_performance",
        "ロボットと会話をするにあたって、あなた自身が想定した作業（指示）は、どの程度ロボットによって達成されたと考えますか？",
    ),
    (
        "nasa_effort",
        "あなたはその作業達成率に到達するのに、どのくらい（精神的および身体的に）努力しましたか？",
    ),
    (
        "nasa_frustration",
        "あなたは、ロボットと会話をするにあたってどのくらい不安，落胆，いらいら，ストレス，不快感を感じましたか？",
    ),
)

GODSPEED_ANTHROPOMORPHISM_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("godspeed_anthroporphism1", "Fake 偽物のような (1) - Natural 自然な (5)"),
    ("godspeed_anthroporphism2", "Machinelike 機械的 (1) - Humanlike 人間的 (5)"),
    ("godspeed_anthroporphism3", "Unconscious 意識を持たない (1) - Contious 意識を持っている (5)"),
    ("godspeed_anthroporphism4", "Artificial 人工的 (1) - Lifelike 生物的 (5)"),
    ("godspeed_anthroporphism5", "Moving rigidly ぎこちない動き (1) - Moving elegantly 洗練された動き (1)"),
)

GODSPEED_ANIMACY_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("godspeed_animacy1", "Dead 死んでいる (1) - Alive 生きている (5)"),
    ("godspeed_animacy2", "Stagnant 活気のない (1) - Lively 生き生きとした (5)"),
    ("godspeed_animacy3", "Mechanical 機械的な (1) - Organic 有機的な (5)"),
    ("godspeed_animacy4", "Inert 不活発な (1) - Interactive 対話的な (5)"),
    ("godspeed_animacy5", "Apathetic 無関心な (1) - Responsive 反応のある (5)"),
)

GODSPEED_LIKEABILITY_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("godspeed_likeability1", "Dislike 嫌い (1) - Like 好き (5)"),
    ("godspeed_likeability2", "Unfriendly 親しみにくい (1) - Friendly 親しみやすい (5)"),
    ("godspeed_likeability3", "Unkind 不親切な (1) - Kind 親切な (5)"),
    ("godspeed_likeability4", "Unpleasant 不愉快な (1) - Pleasant 愉快な (5)"),
    ("godspeed_likeability5", "Awful ひどい (1) - Nice 良い (5)"),
)

GODSPEED_PERCEIVED_INTELLIGENCE_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("godspeed_intelligence1", "Incompetent 無能な (1) - Competent 有能な (5)"),
    ("godspeed_intelligence2", "Ignorant 無知な (1) - Knowledgeable 物知りな (5)"),
    ("godspeed_intelligence3", "Irresponsible 無責任な (1) - Responsible 責任のある (5)"),
    ("godspeed_intelligence4", "Unintelligent 知的でない (1) - Intelligent 知的な (5)"),
    ("godspeed_intelligence5", "Foolish 愚かな (1) - Sensible 賢明な (5)"),
)

GODSPEED_PERCEIVED_SAFETY_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("godspeed_safety1", "Anxious 不安な (1) - Relaxed 落ち着いた (5)"),
    ("godspeed_safety2", "Agitated 動揺している (1) - Calm 冷静な (5)"),
    ("godspeed_safety3", "Quiescent 平穏な (1) - Surprised 驚いた (5)"),
)

TRUST_SCALE_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("trust1", "このロボットは能力が高いと信じる"),
    ("trust2", "私はこのロボットを信頼している"),
    ("trust3", "このロボットの助言（アドバイス）は信頼できる"),
    ("trust4", "私はこのロボットに頼れる"),
    ("trust5", "このロボットの動作（ふるまい）は一貫していると思う"),
    ("trust6", "このロボットの助言に従うとき、このロボットは最善を尽くしてくれると信頼している"),
)

OTHER_QUESTIONS: Tuple[Tuple[str, str], ...] = (
    ("other1", "これからもこのロボットを使いたいと思う"),
)


def _make_key(base: str, key_prefix: str) -> str:
    return f"{base}_{key_prefix}" if key_prefix else base


def _collect_slider_scores(
    questions: Tuple[Tuple[str, str], ...],
    *,
    key_prefix: str,
    min_value: int = 1,
    max_value: int = 5,
) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for key, question in questions:
        scores[key] = st.slider(
            question,
            min_value=min_value,
            max_value=max_value,
            value=3,
            step=1,
            format="%d",
            key=_make_key(key, key_prefix),
        )
    return scores


def render_standard_evaluation_form(
    *,
    prompt_group: str,
    include_sus: bool = False,
    include_trust: bool = True,
    form_key: str = "evaluation_form",
    key_prefix: str | None = None,
    termination_label: str | None = None,
) -> bool:
    """Render the common evaluation form and save the result if submitted.

    Returns
    -------
    bool
        ``True`` when the form was submitted and saved.
    """

    prefix = key_prefix or prompt_group or "experiment"

    with st.form(form_key):
        st.subheader("⑥評価フォーム")
        name = st.text_input("あなたの名前")

        sus_scores: Dict[str, int] = {}
        if include_sus:
            st.markdown("###### SUS（システムユーザビリティ尺度）")
            sus_option_labels = [label for label, _ in SUS_OPTIONS]
            sus_value_map = dict(SUS_OPTIONS)
            for key, question in SUS_QUESTIONS:
                choice = st.radio(
                    question,
                    sus_option_labels,
                    horizontal=True,
                    key=_make_key(key, prefix),
                )
                sus_scores[key] = sus_value_map.get(choice, 0)

        st.markdown("###### NASA TLX（1 = 低い ／ 5 = 高い）")
        nasa_scores = _collect_slider_scores(NASA_TLX_QUESTIONS, key_prefix=prefix)

        st.markdown("###### Godspeed ロボットの印象について")
        st.markdown(
            "**・人間らしさ（Anthropomorphism）**: 以下のスケールに基づいてこのロボットの印象を評価してください。"
        )
        godspeed_anthroporphism_scores = _collect_slider_scores(
            GODSPEED_ANTHROPOMORPHISM_QUESTIONS,
            key_prefix=prefix,
        )

        st.markdown("**・生命感（Animacy）**: 以下のスケールに基づいてこのロボットの印象を評価してください。")
        godspeed_animacy_scores = _collect_slider_scores(
            GODSPEED_ANIMACY_QUESTIONS,
            key_prefix=prefix,
        )

        st.markdown("**・好感度（Likeability）**: 以下のスケールに基づいてこのロボットの印象を評価してください。")
        godspeed_likeability_scores = _collect_slider_scores(
            GODSPEED_LIKEABILITY_QUESTIONS,
            key_prefix=prefix,
        )

        st.markdown(
            "**・知能の知覚（Perceived Intelligence）**: 以下のスケールに基づいてこのロボットの印象を評価してください。"
        )
        godspeed_intelligence_scores = _collect_slider_scores(
            GODSPEED_PERCEIVED_INTELLIGENCE_QUESTIONS,
            key_prefix=prefix,
        )

        st.markdown("**・安全性の知覚（Perceived Safety）**: 以下のスケールに基づいてあなたの心の状態を評価してください。")
        godspeed_safety_scores = _collect_slider_scores(
            GODSPEED_PERCEIVED_SAFETY_QUESTIONS,
            key_prefix=prefix,
        )

        trust_scores: Dict[str, int] = {}
        if include_trust:
            st.markdown("#### 信頼尺度（Trust Scale）")
            trust_scores = _collect_slider_scores(
                TRUST_SCALE_QUESTIONS,
                key_prefix=prefix,
            )

        other_scores: Dict[str, int] = {}
        st.markdown("#### その他の質問")
        other_scores = _collect_slider_scores(
            OTHER_QUESTIONS,
            key_prefix=prefix,
        )

        st.markdown("#### 自由記述")
        impression = st.text_input(
            "AIとの会話や、ロボットの行動計画について「印象に残ったこと」があればお願いします。"
        )
        free = st.text_input("その他に何か感じたことがあればお願いします。")

        submitted = st.form_submit_button("評価を保存", type="primary")

    if not submitted:
        return False

    st.warning("評価を保存しました！適宜休憩をとってください☕")

    godspeed_scores: Dict[str, Dict[str, int]] = {
        "anthropomorphism": godspeed_anthroporphism_scores,
        "animacy": godspeed_animacy_scores,
        "likeability": godspeed_likeability_scores,
        "perceived_intelligence": godspeed_intelligence_scores,
        "perceived_safety": godspeed_safety_scores,
    }

    human_scores: Dict[str, object] = {
        "participant_name": name,
        "sus": sus_scores if include_sus else {},
        "nasatlx": nasa_scores,
        "godspeed": godspeed_scores,
        "trust_scale": trust_scores if include_trust else {},
        "other": other_scores,
        "text_inputs": {
            "impression": impression,
            "free": free,
        },
    }

    if termination_label is None:
        termination_label = (
            "タスク完了ボタンが押されました"
            if st.session_state.get("force_end")
            else ""
        )

    save_experiment_result(
        human_scores,
        prompt_group=prompt_group,
        termination_label=termination_label,
    )

    return True


__all__ = [
    "render_standard_evaluation_form",
    "SUS_OPTIONS",
    "SUS_QUESTIONS",
    "NASA_TLX_QUESTIONS",
    "GODSPEED_ANTHROPOMORPHISM_QUESTIONS",
    "GODSPEED_ANIMACY_QUESTIONS",
    "GODSPEED_LIKEABILITY_QUESTIONS",
    "GODSPEED_PERCEIVED_INTELLIGENCE_QUESTIONS",
    "GODSPEED_PERCEIVED_SAFETY_QUESTIONS",
    "TRUST_SCALE_QUESTIONS",
    "OTHER_QUESTIONS",
]
