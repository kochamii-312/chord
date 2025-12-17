from __future__ import annotations

import streamlit as st

from .tasks import choose_random_task, get_tasks_for_room


def render_random_room_task(
    room_name: str,
    state_prefix: str,
    *,
    title: str = "タスク",
    reroll_label: str = "🔀 他のタスクにする",
) -> str | None:
    """Display a random task for the specified room at the top of the page.

    Args:
        room_name: Room identifier chosen in the UI. Empty string means no selection.
        state_prefix: Prefix used to keep Streamlit session state keys unique per page.
        title: Heading shown above the task suggestion.
        reroll_label: Label for the button to pick another random task.

    Returns:
        The currently displayed random task or ``None`` when there is nothing to show.
    """

    task_state_key = f"{state_prefix}_random_task"
    room_state_key = f"{state_prefix}_task_room"

    if st.session_state.get(room_state_key) != room_name:
        st.session_state[room_state_key] = room_name
        st.session_state[task_state_key] = choose_random_task(room_name)

    st.markdown(f"### {title}")

    if not room_name:
        st.info("部屋を選択すると、タスク候補が表示されます。")
        st.session_state[task_state_key] = None
        return None

    tasks = get_tasks_for_room(room_name)
    if not tasks:
        st.info(f"部屋「{room_name}」に対応するタスク候補は未登録です。")
        st.session_state[task_state_key] = None
        return None

    if st.button(reroll_label, key=f"{state_prefix}_reroll"):
        st.session_state[task_state_key] = choose_random_task(room_name)

    task = st.session_state.get(task_state_key)
    if task:
        st.success(f"部屋「{room_name}」のタスク例：{task}")
    return task


def reset_random_room_task(state_prefix: str) -> None:
    """Re-roll the random task associated with ``state_prefix`` if possible."""

    task_state_key = f"{state_prefix}_random_task"
    room_state_key = f"{state_prefix}_task_room"
    room_name = st.session_state.get(room_state_key, "")

    if room_name:
        st.session_state[task_state_key] = choose_random_task(room_name)
    else:
        st.session_state[task_state_key] = None
