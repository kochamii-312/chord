
# Clarification Dataset Logger

- `clarify_logger.py`: a tiny utility to log conversations into JSONL for Llama fine-tuning.
- `example_entry.json`: one example entry in your requested schema.
- Running `clarify_logger.py` directly will append one demo row to `dataset.jsonl`.

## Quick start

```bash
python clarify_logger.py
# -> creates/append /dataset.jsonl
```

## How to integrate with your chat loop

1) Initialize logger:
```python
from clarify_logger import ClarifyLogger
log = ClarifyLogger()
log.start_dialog(user_instruction)  # first user message
```

2) When assistant asks a question:
```python
log.add_question(assistant_question)
# wait user reply
log.add_user_answer(user_reply)
# decide sufficiency:
# - if the next assistant message is another question -> mark the last as 'insufficient'
# - if the next assistant message contains a <Plan> or final action -> mark as 'sufficient'
log.mark_last_question_label("sufficient" or "insufficient")
```

3) When final answer is produced:
```python
log.set_final_answer(final_text, label="sufficient")
log.save("dataset.jsonl")
```

## Tip: automatic extraction from XML
If your assistant outputs `<ClarificationQuestion>...</ClarificationQuestion>`,
you can detect it with `ClarifyLogger.extract_clarification_question(text)`
and detect plans with `ClarifyLogger.has_plan(text)`.
