import os
from typing import Set
import streamlit as st
from api import build_bootstrap_user_message

ROOM_TOKENS = ["BEDROOM", "KITCHEN", "DINING", "LIVING", "BATHROOM", "和室", "HALL", "LDK"]

def detect_rooms_in_text(text: str) -> Set[str]:
    """Return a set of room tokens found in text."""
    found: Set[str] = set()
    up = (text or "").upper()
    for r in ROOM_TOKENS:
        if r == "和室":
            if "和室" in (text or ""):
                found.add(r)
        else:
            if r in up:
                found.add(r)
    return found

def attach_images_for_rooms(rooms: Set[str], show_in_ui: bool = True) -> None:
    """Attach room images for new rooms to the conversation context and optionally display them."""
    if "sent_room_images" not in st.session_state:
        st.session_state.sent_room_images = set()
    new_rooms = [r for r in rooms if r not in st.session_state.sent_room_images]
    if not new_rooms:
        return