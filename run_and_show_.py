
# run_and_show.py
# Utilities used by experiment pages to (a) parse function sequences from LLM output,
# (b) execute them against move_functions, and (c) show results in Streamlit.
#
# This version supports TWO formats:
#   (A) Preferred: <FunctionSequence> with Python-like calls, e.g.:
#         move("forward", 1.0)
#         rotate("left", 90)
#         go_to_location("キッチン")
#         stop()
#   (B) Fallback XML-ish tags (line or whole text), e.g.:
#         <move_to>storage</move_to>
#         <move>back</move>
#         <rotate>left,90</rotate>
#         <place_object_in>wood,fireplace</place_object_in>  (unsupported → warning)

import re
import ast
import streamlit as st
from typing import Callable, Dict, Any

# Import the four required robot functions
from move_functions import move, rotate, go_to_location, stop, get_log, reset_log

# --- Basic helpers -----------------------------------------------------------

def extract_between(tag: str, text: str) -> str | None:
    m = re.search(fr"<{tag}>([\s\S]*?)</{tag}>", text or "", re.IGNORECASE)
    return m.group(1).strip() if m else None

def strip_tags(text: str) -> str:
    return re.sub(r"</?([A-Za-z0-9_]+)(\s[^>]*)?>", "", text or "").strip()

def _safe_eval_call(expr: str, env: Dict[str, Callable]) -> Any:
    """
    Safely evaluate a single function call like:
      move("forward", 1.0)
      rotate("left", 90)
      go_to_location("キッチン")
      stop()
    Disallow arbitrary code by parsing with ast and only permitting Call nodes.
    """
    try:
        node = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        return f"SyntaxError: {e}"

    if not isinstance(node.body, ast.Call):
        return "NG: Not a function call."

    call = node.body
    # function name must be a Name
    if not isinstance(call.func, ast.Name):
        return "NG: Unsafe function reference."

    fname = call.func.id
    if fname not in env:
        return f"NG: Function '{fname}' not allowed."

    # Evaluate args as Python literals only
    def _eval_arg(arg_node):
        if isinstance(arg_node, (ast.Constant,)):
            return arg_node.value
        elif isinstance(arg_node, ast.UnaryOp) and isinstance(arg_node.op, (ast.UAdd, ast.USub)) and isinstance(arg_node.operand, ast.Constant):
            # allow -1, +1 style
            val = arg_node.operand.value
            return +val if isinstance(arg_node.op, ast.UAdd) else -val
        else:
            raise ValueError("Only literal arguments are allowed.")

    try:
        args = [_eval_arg(a) for a in call.args]
        kwargs = {kw.arg: _eval_arg(kw.value) for kw in call.keywords}
    except Exception as e:
        return f"ArgError: {e}"

    try:
        return env[fname](*args, **kwargs)
    except Exception as e:
        return f"ExecError in {fname}: {e}"

# --- Fallback: simple tag-based parser --------------------------------------

# Map loose direction synonyms
_DIR_MAP = {
    "fwd": "forward", "forward": "forward", "front": "forward", "前": "forward", "前進": "forward",
    "back": "backward", "backward": "backward", "後退": "backward", "後ろ": "backward",
    "left": "left", "leftward": "left", "右": "right", "right": "right", "左": "left",
}

def _fallback_tag_to_call(tag: str, content: str):
    """
    Convert a single XML-ish tag to a canonical function call string.
    Returns a python-call string like: move("forward", 1.0)  or None if unsupported.
    """
    t = tag.lower().strip()
    c = (content or "").strip()

    if t in ("move_to", "goto", "go_to", "go_to_location"):
        # use as location name verbatim
        if not c:
            return None
        return f'go_to_location("{c}")'

    if t in ("move", "walk", "translate"):
        # default distance = 1.0m unless a number is included
        # allow formats: "back", "forward 2", "left, 0.5"
        parts = re.split(r"[,\s]+", c)
        parts = [pp for pp in parts if pp]
        if not parts:
            return None
        direction = parts[0].lower()
        direction = _DIR_MAP.get(direction, direction)
        dist = 1.0
        # look for a numeric token
        for tok in parts[1:]:
            try:
                dist = float(tok)
                break
            except ValueError:
                continue
        return f'move("{direction}", {dist})'

    if t in ("rotate", "turn"):
        # formats: "left,90" or "right 45"
        parts = re.split(r"[,\s]+", c)
        parts = [pp for pp in parts if pp]
        if not parts:
            return None
        direction = _DIR_MAP.get(parts[0].lower(), parts[0].lower())
        angle = 90.0
        for tok in parts[1:]:
            try:
                angle = float(tok)
                break
            except ValueError:
                continue
        return f'rotate("{direction}", {angle})'

    if t in ("stop", "halt"):
        return "stop()"

    # Unsupported but recognized task-level commands
    if t in ("pick_object", "place_object_in", "place_object_on", "pick", "place"):
        # We will render a warning in Streamlit and skip execution
        return f'# UNSUPPORTED({t}): {c}'

    return None

def _extract_all_simple_tags(text: str):
    # Finds all <tag>content</tag> non-greedy, in order.
    pattern = re.compile(r"<([A-Za-z0-9_]+)>([\s\S]*?)</\1>", re.IGNORECASE)
    return pattern.findall(text or "")

def _fallback_parse_whole_reply(text: str):
    # Convert every supported tag we find to a python-call string.
    calls = []
    for tag, content in _extract_all_simple_tags(text or ""):
        call = _fallback_tag_to_call(tag, content)
        if call:
            calls.append(call)
    return calls

# --- Streamlit renderers & runner -------------------------------------------

def show_function_sequence(reply: str):
    """
    If <FunctionSequence> is present, show it in a pretty block for the user.
    """
    fs = extract_between("FunctionSequence", reply or "")
    if not fs:
        return
    st.markdown("##### FunctionSequence")
    st.code(fs.strip(), language="python")

def show_clarifying_question(reply: str):
    q = extract_between("ClarifyingQuestion", reply or "")
    if q:
        st.info(f"🤖 質問: {q}")

def run_plan_and_show(reply: str):
    """
    Execute the function calls in <FunctionSequence> and display a log.
    If no <FunctionSequence> is present, or if individual lines fail with SyntaxError,
    fall back to parsing simple XML-like tags such as <move_to>kitchen</move_to>.
    """
    fs = extract_between("FunctionSequence", reply or "")
    allowed_env = {
        "move": move,
        "rotate": rotate,
        "go_to_location": go_to_location,
        "stop": stop,
    }

    reset_log()
    st.markdown("##### 実行ログ")

    executed_any = False

    def _execute_line(line: str):
        nonlocal executed_any
        line = line.strip()
        if not line or line.startswith("#"):
            return
        res = _safe_eval_call(line, allowed_env)
        if isinstance(res, str) and res.startswith("SyntaxError"):
            # Try fallback conversion for a single-tag line like <move>back</move>
            tags = _extract_all_simple_tags(line)
            if tags:
                some = False
                for t, c in tags:
                    call = _fallback_tag_to_call(t, c)
                    if call:
                        r2 = _safe_eval_call(call, allowed_env)
                        st.write(f"`<{t}>` → `{call}` → **{r2}**")
                        executed_any = True
                        some = True
                    else:
                        st.write(f"`<{t}>` → **未対応コマンド**: {c}")
                if some:
                    return
        st.write(f"`{line}` → **{res}**")
        executed_any = True

    if fs:
        for raw_line in fs.splitlines():
            _execute_line(raw_line)
    else:
        # No FunctionSequence → parse all tags from the whole reply
        calls = _fallback_parse_whole_reply(reply or "")
        if calls:
            for call in calls:
                _execute_line(call)
        else:
            st.write("（実行可能な関数やタグが見つかりませんでした）")
            return

    # show final accumulated log
    logs = get_log()
    if logs:
        st.markdown("##### シミュレータ内部ログ")
        for l in logs:
            st.caption(l)
