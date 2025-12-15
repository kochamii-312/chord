import streamlit as st
import re

TAG_RE = re.compile(r"</?([A-Za-z0-9_]+)(\s[^>]*)?>")

ROOM_TRANSLATIONS = {
    "BATHROOM": "洗面所",
    "KITCHEN": "キッチン",
    "DINING": "ダイニング",
    "LIVING": "リビング",
    "BEDROOM": "寝室",
    "HALL": "廊下",
    "LDK": "LDK",
}

SELF_CLOSING_MOVE_TO_RE = re.compile(r"<move_to\s+room_name=['\"](.*?)['\"]\s*/>", re.IGNORECASE)

def strip_tags(text: str) -> str:
    return TAG_RE.sub("", text or "").strip()

def extract_between(tag: str, text: str) -> str | None:
    m = re.search(fr"<{tag}>([\s\S]*?)</{tag}>", text or "", re.IGNORECASE)
    return m.group(1).strip() if m else None

def _normalize_step(step: str) -> str:
    def repl(match: re.Match) -> str:
        room = match.group(1).strip()
        jp = ROOM_TRANSLATIONS.get(room.upper(), room)
        return f"<move_to>{jp}</move_to>"

    return SELF_CLOSING_MOVE_TO_RE.sub(repl, step)

def parse_step(step):
    step = _normalize_step(step.strip())
    # <move_to>BEDROOM</move_to> → move_to("BEDROOM")
    m = re.match(r"<(\w+)>(.*?)</\1>", step)
    if m:
        func = m.group(1)
        arg = m.group(2).strip()
        # 引数がカンマ区切りの場合も考慮
        args = [a.strip() for a in arg.split(",")] if "," in arg else [arg]
        args_str = ", ".join([f'"{a}"' for a in args])
        return f"{func}({args_str})"
    return step  # それ以外はそのまま
