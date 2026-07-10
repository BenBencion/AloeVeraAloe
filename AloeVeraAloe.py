from datetime import datetime
from telethon import TelegramClient

# ========================= НАСТРОЙКИ =========================
API_ID = 34096249
API_HASH = '2c7bde0885bafb5ecb20d8cbf29d421d'
from datetime import datetime
from telethon import TelegramClient

# ============= НАСТРОЙКИ =============
API_ID = 12345678          # ← твой api_id
API_HASH = "твой_api_hash" # ← твой api_hash
CHANNEL = "@BurkinaFaso11" # или ID канала

# =====================================

client = TelegramClient('time_bot', API_ID, API_HASH)

async def main():
    await client.start()
    
    now = datetime.now()
    time_str = now.strftime("🕒 Сейчас: %d.%m.%Y %H:%M:%S")
    
    await client.send_message(CHANNEL, time_str)
    print("✅ Сообщение с временем отправлено в канал!")

# Запуск
with client:
    client.loop.run_until_complete(main())