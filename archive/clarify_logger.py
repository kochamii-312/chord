
"""
clarify_logger.py

A minimal logger to save conversations for Llama fine-tuning in the schema:

{
  "instruction": "<user's initial request>",
  "clarifying_steps": [
    {
      "llm_question": "...",
      "question_label": "sufficient" | "insufficient",
      "user_answer": "..."
    },
    ...
  ],
  "final_answer": "...",
  "label": "sufficient" | "insufficient"
}

Usage (pseudo):
- Import ClarifyLogger and use .start_dialog(instruction)
- Each time the LLM asks a clarification, call .add_question(q)
- When the user answers, call .add_user_answer(ans)
- When the LLM either asks another clarification or gives final answer, call .mark_last_question_label(...)
- Finish with .set_final_answer(text, label) and .save(dataset_path)

If you use the XML format (<ClarificationQuestion>...</ClarificationQuestion> and <Plan>...</Plan>),
you can parse assistant outputs and call these methods automatically.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Optional
import json
from pathlib import Path
import datetime
import os
import re

from utils.firebase_utils import save_document
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ClarifyingStep:
    llm_question: str
    question_label: str  # "sufficient" or "insufficient"
    user_answer: str


@dataclass
class DialogueSample:
    instruction: str
    clarifying_steps: List[ClarifyingStep] = field(default_factory=list)
    final_answer: str = ""
    label: str = "insufficient"  # overall label


class ClarifyLogger:
    def __init__(self):
        self.current: Optional[DialogueSample] = None
        self._last_open_question_index: Optional[int] = None

    def start_dialog(self, instruction: str):
        """Start a new dialogue sample with the initial instruction."""
        self.current = DialogueSample(instruction=instruction)
        self._last_open_question_index = None

    def add_question(self, question: str):
        """Add a clarification question from the LLM. Marks it as pending until a label is set."""
        if self.current is None:
            raise RuntimeError("Call start_dialog() first.")
        self.current.clarifying_steps.append(ClarifyingStep(
            llm_question=question.strip(),
            question_label="insufficient",  # default until proven sufficient
            user_answer=""
        ))
        self._last_open_question_index = len(self.current.clarifying_steps) - 1

    def add_user_answer(self, answer: str):
        """Attach the user's answer to the last pending question."""
        if self.current is None or self._last_open_question_index is None:
            raise RuntimeError("No pending question to attach the answer to.")
        self.current.clarifying_steps[self._last_open_question_index].user_answer = answer.strip()

    def mark_last_question_label(self, label: str):
        """Mark the last question as 'sufficient' or 'insufficient' given the LLM's next move."""
        if self.current is None or self._last_open_question_index is None:
            raise RuntimeError("No pending question to label.")
        if label not in ("sufficient", "insufficient"):
            raise ValueError("label must be 'sufficient' or 'insufficient'")
        self.current.clarifying_steps[self._last_open_question_index].question_label = label

        # once labeled, close it
        self._last_open_question_index = None

    def set_final_answer(self, text: str, label: str = "sufficient"):
        """Set the final answer and overall label for the sample."""
        if self.current is None:
            raise RuntimeError("Call start_dialog() first.")
        if label not in ("sufficient", "insufficient"):
            raise ValueError("label must be 'sufficient' or 'insufficient'")
        self.current.final_answer = text.strip()
        self.current.label = label

    def to_dict(self):
        if self.current is None:
            raise RuntimeError("No current dialogue.")
        return asdict(self.current)

    def save(self, jsonl_path: str):
        """Append the current sample to a JSONL file and optionally Firestore."""
        if self.current is None:
            raise RuntimeError("No current dialogue to save.")

        if jsonl_path:
            Path(jsonl_path).parent.mkdir(parents=True, exist_ok=True)
            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(self.to_dict(), ensure_ascii=False) + "\n")

        firebase_collection = os.getenv("FIREBASE_COLLECTION")
        firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")
        if firebase_collection and firebase_credentials:
            save_document(firebase_collection, self.to_dict(), firebase_credentials)

    # ---- Helpers to parse XML-style assistant outputs and automate logging ----

    @staticmethod
    def extract_clarification_question(assistant_text: str) -> Optional[str]:
        """
        If assistant output contains <ClarificationQuestion>...</ClarificationQuestion>,
        return the inner text. Otherwise None.
        """
        m = re.search(r"<ClarificationQuestion>(.*?)</ClarificationQuestion>", assistant_text, re.S)
        if m:
            return m.group(1).strip()
        return None

    @staticmethod
    def has_plan(assistant_text: str) -> bool:
        """Return True if a <Plan>...</Plan> block is present."""
        return bool(re.search(r"<Plan>(.*?)</Plan>", assistant_text, re.S))


# ---------------------- Demo to produce one JSONL row ----------------------
if __name__ == "__main__":
    logger = ClarifyLogger()
    logger.start_dialog("あれをちょっと横にずらして")

    # Assistant asks a clarification
    logger.add_question("『あれ』とはどの物を指していますか？")
    logger.add_user_answer("青い箱です")
    # After the user's answer, assistant still needs more info -> insufficient
    logger.mark_last_question_label("insufficient")

    # Assistant asks another clarification
    logger.add_question("『横』とは右側ですか、左側ですか？")
    logger.add_user_answer("右側です")
    # Now it will be enough -> sufficient
    logger.mark_last_question_label("sufficient")

    # Final answer
    logger.set_final_answer("青い箱を右に移動します", label="sufficient")

    out = "dataset.jsonl"
    logger.save(out)
    print(f"Wrote one sample to {out}")
