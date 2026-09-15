import re


SPEAKER_PATTERN = re.compile(r"^\s*(Interviewer|Candidate|Recruiter|Applicant)\s*:\s*(.*)$", re.I)


def normalize_transcript(transcript: str) -> str:
    transcript = transcript.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in transcript.splitlines()]
    return "\n".join(line for line in lines if line)


def parse_turns(transcript: str) -> list[dict]:
    text = normalize_transcript(transcript)
    turns = []
    current = None

    for line in text.splitlines():
        match = SPEAKER_PATTERN.match(line)
        if match:
            speaker = match.group(1).lower()
            speaker = "interviewer" if speaker in {"interviewer", "recruiter"} else "candidate"
            if current:
                turns.append(current)
            current = {"speaker": speaker, "text": match.group(2).strip()}
        elif current:
            current["text"] += " " + line

    if current:
        turns.append(current)

    return turns
