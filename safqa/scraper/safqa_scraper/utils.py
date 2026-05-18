import re


def parse_budget(raw: str | None) -> float | None:
    if not raw:
        return None

    s = raw.strip()

    s = re.sub(r"(?i)\b(?:MAD|DH|Dhs)\b", "", s).strip()
    s = s.replace("\u00a0", " ").strip()

    if re.search(r",\d{1,2}$", s):
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")

    s = re.sub(r"[^\d.]", "", s)

    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None
