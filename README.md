# Fast Sticker Bot

A Telegram bot for creating and managing sticker packs much faster than other bots.

Running instance: [@faststicker_bot](https://t.me/faststicker_bot)

## Features

- **Create sticker packs** — `/new_pack`
- **Add stickers** to existing packs — `/add_sticker`
- **Delete sticker packs** — `/del_pack`
- **List your packs** — `/my_packs`

Supported sticker types:
- **Static** — images, photos, stickers
- **Video** — animations, GIFs, MP4 (auto-converted to WEBM via ffmpeg)
- **Animated (TGS)** — Telegram animated sticker format

Images are automatically resized to 512×512 while preserving aspect ratio.

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | List of commands |
| `/about` | Bot info |
| `/new_pack` | Create a new sticker pack |
| `/add_sticker` | Add stickers to an existing pack |
| `/del_pack` | Delete a sticker pack |
| `/my_packs` | List your sticker packs |
| `/cancel` | Cancel current operation |
| `/copy_emoji` | Toggle auto-copying emoji from existing stickers |

## Running

### Docker (recommended)

```bash
git clone <repo-url>
cd faststickerbot
echo "BOT_TOKEN=your_token_here" > .env
docker compose up -d
```

### Manual

```bash
pip install -r requirements.txt
# ffmpeg is required
echo "BOT_TOKEN=your_token_here" > .env
python main.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | Yes | Telegram Bot API token from @BotFather |

## Stack

- Python 3.14
- aiogram 3.27
- SQLite (aiosqlite)
- Pillow (image processing)
- ffmpeg (video conversion)

## File structure

```
cogs/             # Command handlers
utils/            # Core logic
  stores/         # Config, states, types
  integrations/   # Database, video conversion
  service.py      # Bot class
  cog.py          # Cog framework
  shortcuts.py    # Utilities
main.py           # Entry point
```
