import asyncio
import io
from datetime import datetime
from telethon import TelegramClient, types
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ========================= НАСТРОЙКИ =========================
api_id = 34096249
api_hash = '2c7bde0885bafb5ecb20d8cbf29d421d'
channel_username = '@BurkinaFaso11'

BOT_TOKEN = '8258065758:AAF6tc5-4reHZNQGRE2XdOVPkCUZcpJVMo4'

# Ссылка на главную папку Google Drive
FOLDER_LINK = "https://drive.google.com/drive/folders/1U0EgoAyURcrr0PsOuWdk2kZQ5Ou6t2Rv"

# ============================================================

client = TelegramClient('gdrive_sender', api_id, api_hash)


async def get_caption_from_gdoc(service, folder_id):
    """Ищет Google Doc и возвращает его текст как caption"""
    query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    docs = results.get('files', [])

    if not docs:
        return f"📅 Сегодня {datetime.now().strftime('%d %B %Y')}"

    doc_id = docs[0]['id']
    try:
        request = service.files().export_media(fileId=doc_id, mimeType='text/plain')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        fh.seek(0)
        caption = fh.read().decode('utf-8').strip()
        return caption if caption else f"📅 Сегодня {datetime.now().strftime('%d %B %Y')}"
    except Exception as e:
        print(f"❌ Ошибка чтения Google Doc: {e}")
        return f"📅 Сегодня {datetime.now().strftime('%d %B %Y')}"


async def send_all_files_as_album(service, folder_id, day):
    """Отправка альбома с caption из Google Doc"""
    caption = await get_caption_from_gdoc(service, folder_id)

    query = f"'{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])

    if not files:
        await client.send_message(channel_username, f"📂 Папка на {day} число пуста.")
        return

    media_list = []
    print(f"📥 Подготовка {len(files)} файлов...")

    for file in files:
        try:
            mime = file.get('mimeType', '')
            if mime == 'application/vnd.google-apps.document':
                continue  # Пропускаем Google Doc

            request = service.files().get_media(fileId=file['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            fh.seek(0)

            uploaded = await client.upload_file(fh, file_name=file['name'])

            if mime.startswith('image/'):
                media = types.InputMediaUploadedPhoto(file=uploaded)
                media_list.append(media)

            elif mime.startswith('video/'):
                media = types.InputMediaUploadedDocument(
                    file=uploaded,
                    mime_type=mime or 'video/mp4',
                    attributes=[
                        types.DocumentAttributeVideo(
                            duration=0,
                            w=1080,
                            h=1920,
                            supports_streaming=True
                        )
                    ]
                )
                media_list.append(media)

            else:
                await client.send_file(channel_username, uploaded, filename=file['name'])
                await asyncio.sleep(1)
                continue

        except Exception as e:
            print(f"❌ Ошибка подготовки {file['name']}: {e}")

    if media_list:
        await client.send_file(
            channel_username,
            file=media_list,
            caption=caption,
            parse_mode='html'
        )
        print(f"✅ Отправлен медиа-альбом за {day} число ({len(media_list)} файлов)")
    else:
        await client.send_message(channel_username, f"📭 В папке {day} нет фото или видео.")


async def main():
    await client.start(bot_token=BOT_TOKEN)
    print("🤖 Бот запущен...")

    creds = Credentials.from_authorized_user_file('token.json', 
        ['https://www.googleapis.com/auth/drive.readonly'])
    service = build('drive', 'v3', credentials=creds)

    while True:
        today = datetime.now().day
        print(f"🔍 Проверка: сегодня {today} число...")

        query = f"name='{today}' and mimeType='application/vnd.google-apps.folder' and '{FOLDER_LINK.split('/')[-1]}' in parents"
        results = service.files().list(q=query, fields="files(id, name)").execute()
        folders = results.get('files', [])

        if folders:
            await send_all_files_as_album(service, folders[0]['id'], today)
        else:
            print(f"Папка {today} не найдена.")

        await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(main())
