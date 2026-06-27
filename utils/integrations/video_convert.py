import os
import subprocess
import tempfile


def convert_to_webm(
    input_bytes: bytes,
    suffix: str = ".mp4",
    max_size_kb: int = 256,
    max_duration: int = 3,
) -> bytes:
    """
    Convert video bytes to Telegram-compatible WEBM bytes using ffmpeg.
    Returns WEBM file bytes or raises Exception on failure.
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as input_file:
        input_file.write(input_bytes)
        input_file.flush()
        input_path = input_file.name
    webm_path = input_path.replace(suffix, ".webm")
    try:
        for bitrate in ["350K", "250K", "180K", "120K", "80K"]:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-c:v",
                "libvpx-vp9",
                "-b:v",
                bitrate,
                "-an",
                "-vf",
                "scale=512:512:force_original_aspect_ratio=decrease,fps=30",
                "-t",
                str(max_duration),
                "-pix_fmt",
                "yuva420p",
                webm_path,
            ]
            subprocess.run(
                cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if os.path.exists(webm_path):
                size_kb = os.path.getsize(webm_path) // 1024
                if size_kb <= max_size_kb:
                    break
        else:
            raise Exception(
                f"Cannot fit webm under {max_size_kb}KB, try a shorter or simpler video."
            )
        with open(webm_path, "rb") as webm_file:
            webm_bytes = webm_file.read()
    finally:
        os.remove(input_path)
        if os.path.exists(webm_path):
            os.remove(webm_path)
    return webm_bytes
