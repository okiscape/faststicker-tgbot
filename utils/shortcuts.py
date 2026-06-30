import io
import re
from datetime import datetime

from PIL import Image

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001f300-\U0001f3fa"  # Emoji blocks (excl. skin tone modifiers 1F3FB-1F3FF)
    "\U0001f400-\U0001faff"
    "\U0001f1e0-\U0001f1ff"  # Regional Indicators (flag letters)
    "\U00002600-\U000027bf"  # Misc Symbols + Dingbats
    "\U0000231a-\U0000231b"  # Watch, Hourglass
    "\U000023e9-\U000023f3"  # Time/Media buttons
    "\U000025aa-\U000025ab"  # Small squares
    "\U000025b6"  # Triangle
    "\U000025c0"  # Triangle
    "\U000025fb-\U000025fe"  # Medium squares
    "\U00002b05-\U00002b07"  # Arrows
    "\U00002b1b-\U00002b1c"  # Large squares
    "\U00002b50"  # Star
    "\U00002b55"  # Circle
    "\U00003030"  # Wavy dash
    "\U0000303d"  # Part alternation mark
    "\U00003297"  # Congratulation ideograph
    "\U00003299"  # Secret ideograph
    "\U000000a9"  # Copyright
    "\U000000ae"  # Registered
    "\U00002122"  # Trade mark
    "\U00002139"  # Information source
    "\U00002194-\U00002199"  # Arrows
    "\U000021a9-\U000021aa"  # Arrows
    "\U00002328"  # Keyboard
    "\U000023cf"  # Eject
    "\U000023f8-\U000023fa"  # Media controls
    "\U000024c2"  # Enclosed M
    "\U00002934-\U00002935"  # Arrows
    "\U0000203c"  # Double exclamation mark
    "\U00002049"  # Exclamation question mark
    "]+"
)


def is_emoji(text: str) -> bool:
    if not text:
        return False
    return bool(_EMOJI_PATTERN.fullmatch(text))


def fitImage(img: io.BytesIO, max_size=512) -> Image.Image:
    img: Image.Image = Image.open(img)
    scale = max_size / max(img.width, img.height)
    new_width = int(img.width * scale)
    new_height = int(img.height * scale)
    img = img.resize((new_width, new_height), Image.Resampling.BILINEAR)
    return img


def getNowDTTS() -> int:
    return int(datetime.utcnow().timestamp())
