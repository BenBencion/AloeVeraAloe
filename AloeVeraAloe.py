import asyncio
import io
import sys
from datetime import datetime, timedelta

from PIL import Image, ImageOps
from telethon import TelegramClient, types
from telethon.errors import SessionPasswordNeededError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ========================= НАСТРОЙКИ =========================
API_ID = 34096249
API_HASH = '2c7bde0885bafb5ecb20d8cbf29d421d'
SESSION_NAME = 'session_name'

TARGET_CHAT = '@Vera_vsebya_zanyata'

FOLDER_LINK = "https://drive.google.com/drive/folders/1U0EgoAyURcrr0PsOuWdk2kZQ5Ou6t2Rv"

SCHEDULER_HOUR = 15
SCHEDULER_MINUTE = 10
# ============================================================

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive.readonly'])
service = build('drive', 'v3', credentials=creds)


# ====================== АВТОРИЗАЦИЯ ======================
async def interactive_auth():
    """Интерактивная авторизация с подсказками"""
    print("\n" + "="*50)
    print("🔐 НАЧИНАЕМ АВТОРИЗАЦИЮ TELETHON")
    print("="*50)

    try:
        # Пробуем подключиться
        await client.connect()

        if not await client.is_user_authorized():
            print("📱 Пользователь не авторизован. Начинаем вход...")

            # Запрашиваем номер телефона
            phone = input("Введите номер телефона (+7915XXXXXXXXX): ").strip()
            
            await client.sign_in(phone=phone)
            print("✅ Код подтверждения отправлен в Telegram.")

            # Запрашиваем код
            code = input("Введите код подтверждения из Telegram: ").strip()
            await client.sign_in(phone=phone, code=code)

            print("✅ Код принят!")

        # Если включена 2FA
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Успешная авторизация как {me.first_name} (@{me.username})")
            return True
        else:
            # Запрашиваем 2FA пароль
            print("🔒 Требуется двухфакторная аутентификация")
            password = input("Введите 2FA-пароль: ").strip()
            await client.sign_in(password=password)
            print("✅ 2FA успешно пройдена!")

        return True

    except SessionPasswordNeededError:
        password = input("🔒 Введите 2FA-пароль: ").strip()
        await client.sign_in(password=password)
        print("✅ 2FA успешно пройдена!")
        return True

    except Exception as e:
        print(f"❌ Ошибка авторизации: {e}")
        return False


# ====================== ОСНОВНЫЕ ФУНКЦИИ ======================
def prepare_image_for_telegram(input_bytes: io.BytesIO) -> io.BytesIO:
    input_bytes.seek(0)
    img = Image.open(input_bytes)

    try:
        img = ImageOps.exif_transpose(img)
    except:
        pass

    if img.mode != "RGB":
        img = img.convert("RGB")

    max_size = 2560
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=90, optimize=True)
    output.seek(0)
    return output


# ... (остальные функции get_files_from_day_folder и send_scheduled_post остаются без изменений) ...


async def main():
    print("🚀 Запуск Userbot...")

    # Интерактивная авторизация
    auth_success = await interactive_auth()
    
    if not auth_success:
        print("❌ Авторизация не удалась. Завершение.")
        return

    print("✅ Бот успешно авторизован и запущен!")
    
    asyncio.create_task(scheduler())
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Бот остановлен пользователем.")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")