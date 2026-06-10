import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from RessoMusic.utils.formatters import time_to_seconds
from RessoMusic import LOGGER

# Safe extraction params to fetch raw format directly
ytdl_audio_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
}

class YouTubeAPI:
    def __init__(self):
        self.base = "https://youtube.com"
        self.regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/ ]{11})"

    async def exists(self, link: str, video_id: Union[bool, str] = None) -> bool:
        if video_id:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_or_text: Union[Message, str]) -> Union[str, bool]:
        if isinstance(message_or_text, str):
            text = message_or_text
        else:
            text = message_or_text.text or ""
            if message_or_text.entities:
                for entity in message_or_text.entities:
                    if entity.type == MessageEntityType.URL:
                        text = text[entity.offset:entity.offset + entity.length]
                        break
        match = re.search(self.regex, text)
        if match:
            return f"https://youtube.com{match.group(1)}"
        return False

    async def download_song(self, link: str) -> str:
        video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
        DOWNLOAD_DIR = "downloads"
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")

        if os.path.exists(file_path):
            return file_path

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                lambda: yt_dlp.YoutubeDL(ytdl_audio_opts).download([f"https://youtube.com{video_id}"])
            )
            return file_path
        except Exception:
            return None
