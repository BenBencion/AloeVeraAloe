import asyncio
import io
from datetime import datetime, timedelta

from PIL import Image, ImageOps
from telethon import TelegramClient, types
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ========================= НАСТРОЙКИ =========================
API_ID = 34096249
API_HASH = '2c7bde0885bafb5ecb20d8cbf29d421d'
from datetime import datetime
from telethon import TelegramClient




from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession

# ================= НАСТРОЙКИ =================
BOT_TOKEN = "8258065758:AAF6tc5-4reHZNQGRE2XdOVPkCUZcpJVMo4"  # ← твой бот токен

CHANNEL = "@BurkinaFaso11"   # или ID канала (-100xxxxxxxxx)
# ============================================

# Создаём клиент для бота
client = TelegramClient(
    StringSession(), 
    api_id=API_ID, 
    api_hash=API_HASH
)

async def main():
    # Подключаемся через Bot Token
    await client.start(bot_token=BOT_TOKEN)
    
    now = datetime.now()
    time_str = now.strftime("🕒 Сейчас: %d.%m.%Y %H:%M:%S")
    
    try:
        await client.send_message(CHANNEL, time_str)
        print("✅ Сообщение успешно отправлено в канал!")
    except Exception as e:
        print("❌ Ошибка:", e)

# Запуск
with client:
    client.loop.run_until_complete(main())