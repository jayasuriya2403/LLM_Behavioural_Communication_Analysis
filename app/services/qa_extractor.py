from app.schemas.analysis import QAItem
from app.services.transcript_processor import parse_turns


def extract_question_answers(transcript: str) -> list[QAItem]:
    turns = parse_turns(transcript)
    items = []
    pending_question = None
    q_no = 0

    for turn in turns:
        if turn["speaker"] == "interviewer":
            pending_question = turn["text"]
        elif turn["speaker"] == "candidate" and pending_question:
            q_no += 1
            items.append(
                QAItem(
                    question_id=f"Q{q_no:02d}",
                    question=pending_question,
                    answer_id=f"A{q_no:02d}",
                    answer=turn["text"],
                )
            )
            pending_question = None

    return items
