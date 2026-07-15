LINE = "━━━━━━━━━━━━━━━━━━━━"


def card(title: str, body: str) -> str:
    return f"{LINE}\n<b>{title}</b>\n{LINE}\n\n{body}"


def progress(value: int, target: int, blocks: int = 10) -> str:
    ratio = min(max(value / target, 0), 1) if target else 0
    full = round(ratio * blocks)
    return "█" * full + "░" * (blocks - full)
