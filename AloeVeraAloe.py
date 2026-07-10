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
SESSION_NAME = 'session_name'

#TARGET_CHAT = '@BurkinaFaso11'
TARGET_CHAT = '@Vera_vsebya_zanyata'


FOLDER_LINK = "https://drive.google.com/drive/folders/1U0EgoAyURcrr0PsOuWdk2kZQ5Ou6t2Rv"
# ============================================================

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive.readonly'])
service = build('drive', 'v3', credentials=creds)


def extract_folder_id(folder_link: str) -> str:
    try:
        if 'folders/' in folder_link:
            return folder_link.split('folders/')[-1].split('?')[0].split('/')[0]
        return folder_link
    except:
        return folder_link


FOLDER_ID = extract_folder_id(FOLDER_LINK)


def prepare_image_for_telegram(input_bytes: io.BytesIO) -> io.BytesIO:
    """Твой вариант обработки изображений"""
    input_bytes.seek(0)
    img = Image.open(input_bytes)

    # 1. Исправляем ориентацию (EXIF)
    try:
        img = ImageOps.exif_transpose(img)
    except:
        pass

    # 2. Конвертируем в RGB
    if img.mode != "RGB":
        img = img.convert("RGB")

    # 3. Изменяем размер (вписываем в квадрат)
    max_size = 2560
    img.thumbnail((max_size, max_size))

    # 4. Сохраняем в JPEG
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=90)
    output.seek(0)
    
    return output


async def get_files_from_day_folder():
    today = datetime.now().day
    print(f"🔍 Проверка: сегодня {today} число...")

    try:
        query_folder = f"name='{today}' and mimeType='application/vnd.google-apps.folder' and '{FOLDER_ID}' in parents and trashed=false"
        results = service.files().list(q=query_folder, fields="files(id, name)").execute()
        folders = results.get('files', [])

        if not folders:
            print(f"⚠️ Подпапка {today} не найдена.")
            return None, []

        day_folder_id = folders[0]['id']
        print(f"✅ Найдена папка: {today}")

        query = f"'{day_folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name, mimeType)", orderBy="name").execute()
        files = results.get('files', [])

        caption = None
        media_list = []

        for file in files:
            mime = file['mimeType']
            name = file['name']

            if mime == 'application/vnd.google-apps.document':
                print(f"📝 Найден документ: {name}")
                request = service.files().export_media(fileId=file['id'], mimeType='text/plain')
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)
                caption = fh.read().decode('utf-8').strip()

            elif mime.startswith('image/'):
                print(f"🖼️  Обрабатываем фото: {name}")
                request = service.files().get_media(fileId=file['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)

                # ←←← ТВОЙ КОД ОБРАБОТКИ
                processed = prepare_image_for_telegram(fh)
                
                uploaded = await client.upload_file(processed, file_name=name)
                media = types.InputMediaUploadedPhoto(file=uploaded)
                media_list.append(media)

            elif mime.startswith('video/'):
                print(f"🎥 Видео: {name}")
                request = service.files().get_media(fileId=file['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                fh.seek(0)

                uploaded = await client.upload_file(fh, file_name=name)
                media = types.InputMediaUploadedDocument(
                    file=uploaded,
                    mime_type=mime or 'video/mp4',
                    attributes=[types.DocumentAttributeVideo(duration=0, supports_streaming=True)]
                )
                media_list.append(media)

        if not caption:
            caption = f"📅 Сегодня {datetime.now().strftime('%d %B %Y')}"

        return caption, media_list

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None, []


async def send_scheduled_post():
    try:
        caption, media_list = await get_files_from_day_folder()
        if not media_list:
            print("⚠️ Нет медиафайлов.")
            return

        print(f"📤 Отправляем {len(media_list)} файлов...")

        schedule_time = datetime.now().replace(hour=0, minute=35, second=0, microsecond=0)
        if schedule_time < datetime.now():
            schedule_time += timedelta(days=1)

        await client.send_file(
            entity=TARGET_CHAT,
            file=media_list,
            caption=caption,
            parse_mode='html',
            schedule=schedule_time,
        )

        print(f'✅ Альбом успешно отложен на {schedule_time.strftime("%d.%m %H:%M")}')

    except Exception as e:
        print(f'❌ Ошибка при отправке: {e}')


# ====================== РАСПИСАНИЕ ======================
async def scheduler():
    print("🕒 Планировщик запущен...")
    while True:
        now = datetime.now()
        if now.hour == 15 and now.minute == 10 and now.second == 0:
            print(f"🕕 Запуск в {now.strftime('%H:%M')}")
            await send_scheduled_post()
            await asyncio.sleep(70)
        await asyncio.sleep(1)


async def main():
    await client.start(phone=lambda: '+84923903192', password=lambda: '11112222')
    print('🤖 Бот успешно запущен!')
    asyncio.create_task(scheduler())
    await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен.")
    except Exception as e:
        print(f"Критическая ошибка: {e}")