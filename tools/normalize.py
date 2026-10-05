"""İsim normalizasyonu. game/scripts/normalize.gd ile birebir aynı davranmalı."""
import re, unicodedata

_TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")

def normalize(s: str) -> str:
    s = s.translate(_TR)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()
