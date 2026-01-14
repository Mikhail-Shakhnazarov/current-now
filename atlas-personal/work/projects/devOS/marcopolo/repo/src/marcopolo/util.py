import hashlib
from typing import Dict, List, Optional, Tuple

REPAIR_TABLE: Dict[str, str] = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "--",
    "\u2014": "--",
    "\u00a0": " ",
}

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def normalize_ascii(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = "\n".join([ln.rstrip() for ln in s.split("\n")])
    return s

def airlock_text(s: str, repair_common_punct: bool = False) -> Tuple[Optional[str], dict]:
    non_ascii = [(i, ch) for i, ch in enumerate(s) if ord(ch) > 127]
    if not non_ascii:
        return s, {"ascii_ok": True, "repaired": False, "non_ascii": []}

    if not repair_common_punct:
        return None, {
            "ascii_ok": False,
            "repaired": False,
            "non_ascii": [
                {"pos": i, "char": ch, "codepoint": f"U+{ord(ch):04X}"}
                for i, ch in non_ascii[:200]
            ],
        }

    out_chars: List[str] = []
    repairs: List[dict] = []
    for i, ch in enumerate(s):
        if ord(ch) <= 127:
            out_chars.append(ch)
            continue
        repl = REPAIR_TABLE.get(ch)
        if repl is None:
            return None, {
                "ascii_ok": False,
                "repaired": False,
                "non_ascii": [{"pos": i, "char": ch, "codepoint": f"U+{ord(ch):04X}"}],
            }
        out_chars.append(repl)
        repairs.append({"pos": i, "from": f"U+{ord(ch):04X}", "to": repl})

    return "".join(out_chars), {
        "ascii_ok": True,
        "repaired": True,
        "repairs": repairs,
        "non_ascii": [{"pos": i, "codepoint": f"U+{ord(ch):04X}"} for i, ch in non_ascii[:200]],
    }
