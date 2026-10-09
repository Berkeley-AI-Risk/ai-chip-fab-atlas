"""Small LaTeX-formatting helpers shared by the report generator."""

UNICODE_REPLACEMENTS = {
    "–": "--",
    "—": "---",
    "−": "-",
    "‑": "-",
    "“": "``",
    "”": "''",
    "‘": "`",
    "’": "'",
    "…": r"\ldots{}",
    "™": r"\texttrademark{}",
    "®": r"\textregistered{}",
    "°": r"\ensuremath{^\circ}",
    "≥": r"\ensuremath{\geq}",
    "≤": r"\ensuremath{\leq}",
    "μ": r"\ensuremath{\mu}",
    "µ": r"\ensuremath{\mu}",
    "×": r"\ensuremath{\times}",
}


def tex(value: object) -> str:
    text = str(value or "")
    for source, target in UNICODE_REPLACEMENTS.items():
        text = text.replace(source, target)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    tokens: dict[str, str] = {}
    for index, command in enumerate(
        sorted(set(UNICODE_REPLACEMENTS.values()), key=len, reverse=True)
    ):
        key = f"@@LATEX{index}@@"
        if command in text:
            text = text.replace(command, key)
            tokens[key] = command
    text = "".join(replacements.get(character, character) for character in text)
    for key, command in tokens.items():
        text = text.replace(key, command)
    return text


def prose_label(value: object) -> str:
    return tex(str(value or "").replace("_", " "))
