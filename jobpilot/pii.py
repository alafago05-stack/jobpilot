"""Local, deterministic PII masking. Runs BEFORE any text reaches an LLM."""
import re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_URL = re.compile(r"(?:https?://|www\.)\S+|(?:linkedin|github)\.com/\S+", re.I)
_PHONE = re.compile(r"(?<![\w/])\+?\(?\d[\d\s().-]{7,}\d")
_NAME_LINE = re.compile(r"^[A-ZÀ-Ý][\w'’-]+(?:\s+[A-ZÀ-Ý][\w'’-]+){1,3}$")


def _digits(s: str) -> int:
    return sum(c.isdigit() for c in s)


def sanitize(text: str, names=()):
    """Return (masked_text, mapping). mapping is kept locally to restore outputs."""
    mapping: dict[str, str] = {}
    counts: dict[str, int] = {}

    def token(label: str, value: str) -> str:
        for k, v in mapping.items():
            if v == value:
                return k
        counts[label] = counts.get(label, 0) + 1
        key = f"[{label}_{counts[label]}]"
        mapping[key] = value
        return key

    candidates = list(names)
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    if _NAME_LINE.match(first):
        candidates.append(first)
    for name in sorted({n for n in candidates if n}, key=len, reverse=True):
        pat = re.compile(re.escape(name), re.I)
        if pat.search(text):
            text = pat.sub(token("NAME", name), text)

    text = _EMAIL.sub(lambda m: token("EMAIL", m.group()), text)
    text = _URL.sub(lambda m: token("URL", m.group()), text)
    text = _PHONE.sub(
        lambda m: token("PHONE", m.group()) if _digits(m.group()) >= 9 else m.group(), text
    )
    return text, mapping


def restore(text: str, mapping: dict) -> str:
    for key, value in mapping.items():
        text = text.replace(key, value)
    return text
