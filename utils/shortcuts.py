import io
import re
from datetime import datetime

from PIL import Image


def is_emoji(character: str) -> bool:
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f"  # Emoticons
        "\U0001f300-\U0001f5ff"  # Symbols & Pictographs
        "\U0001f680-\U0001f6ff"  # Transport & Map Symbols
        "\U0001f700-\U0001f77f"  # Alchemical Symbols
        "\U0001f780-\U0001f7ff"  # Geometric Shapes Extended
        "\U0001f800-\U0001f8ff"  # Supplemental Arrows-C
        "\U0001f900-\U0001f9ff"  # Supplemental Symbols and Pictographs
        "\U0001fa00-\U0001fa6f"  # Chess Symbols
        "\U0001fa70-\U0001faff"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027b0"  # Dingbats
        "\U000024c2-\U0001f251"  # Enclosed Characters
        "]+",
        flags=re.UNICODE,
    )
    return bool(emoji_pattern.match(character))


def fitImage(img: io.BytesIO, max_size=512) -> Image.Image:
    img: Image.Image = Image.open(img)
    scale = max_size / max(img.width, img.height)
    new_width = int(img.width * scale)
    new_height = int(img.height * scale)
    img = img.resize((new_width, new_height), Image.Resampling.BILINEAR)
    return img


def getNowDTTS() -> int:
    return int(datetime.utcnow().timestamp())


def rwc(
    forms: list[str, str, str],
    number: int,
) -> str:
    """
    forms = ["яблоко", "яблок", "яблока"]
    """

    units = number % 10
    tens = number % 100 - units
    if tens == 10 or units >= 5 or units == 0:
        needed_form = 1
    elif units > 1:
        needed_form = 2
    else:
        needed_form = 0
    return forms[needed_form]
