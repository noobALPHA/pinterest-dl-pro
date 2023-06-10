import asyncio
import importlib
import logging
import math
import os
import re
import time
from typing import List
from urllib import request

import aiohttp
import pymongo
import requests
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pymongo import MongoClient
from pyquery import PyQuery as pq
from telethon import TelegramClient, events
from telethon.sync import TelegramClient
from telethon.tl.custom import Button
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import DocumentAttributeVideo

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)
logger = logging.getLogger(__name__)


# Function to get download url
async def get_download_url(link):
    # Make request to website
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://www.pinterestvideodownloader.com/download.php", data={"url": link}
        ) as response:
            # Get content from post request
            request_content = await response.read()
            str_request_content = str(request_content, "utf-8")
            return pq(str_request_content)("table.table-condensed")("tbody")("td")(
                "a"
            ).attr("href")


# Function to download video
async def download_video(url):
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            video_to_download = await response.read()
            with open(
                TMP_DOWNLOAD_DIRECTORY + "pinterest_video.mp4", "wb"
            ) as video_stream:
                video_stream.write(video_to_download)
    return TMP_DOWNLOAD_DIRECTORY + "pinterest_video.mp4"


# Function to download image
async def download_image(url):
    if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(TMP_DOWNLOAD_DIRECTORY)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_to_download = await response.read()
            with open(
                TMP_DOWNLOAD_DIRECTORY + "pinterest_iamge.jpg", "wb"
            ) as photo_stream:
                photo_stream.write(image_to_download)
    return TMP_DOWNLOAD_DIRECTORY + "pinterest_iamge.jpg"


API_ID = os.environ.get("API_ID", None)
API_HASH = os.environ.get("API_HASH", None)
BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
TMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY", "./DOWNLOADS/")
MONGO_DB = os.environ.get("MONGO_DB", None)
LOG = os.environ.get("LOG", None)
OWNER = os.environ.get("OWNER", "ALPHA099")
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/ChatHUB_x_D")
LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID", None))

bot = TelegramClient("pinterestbot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

msg = """

ʜᴇʟʟᴏ ʙᴀʙʏ, 

`ɪ'ᴍ ᴀ ʙᴏᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴠɪᴅᴇᴏs ᴀɴᴅ ɪᴍᴀɢᴇs ғʀᴏᴍ` Pinterest.com

๏ ᴍʏ ᴄᴏᴍᴍᴀɴᴅs

➻ **ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴀ ᴠɪᴅᴇᴏ:** `/vid PinterestURL`

➻ **ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴀ ɪᴍᴀɢᴇ:** `/img PinterestURL`

мα∂є ωιтн 🖤 ву: [˹ᴧŁþнᴧ ꭙ˼](tg://user?id=1057412250) ...!!
"""


SESSION_ADI = "pinterest"


class pinterest_db:
    def __init__(self):
        client = pymongo.MongoClient(MONGO_DB)
        db = client["Telegram"]
        self.collection = db[SESSION_ADI]

    def ara(self, sorgu: dict):
        say = self.collection.count_documents(sorgu)
        if say == 1:
            return self.collection.find_one(sorgu, {"_id": 0})
        elif say > 1:
            cursor = self.collection.find(sorgu, {"_id": 0})
            return {
                bak["u_ID"]: {"u_usr": bak["u_usr"], "u_name": bak["u_name"]}
                for bak in cursor
            }
        else:
            return None

    def ekle(self, u_ID, u_usr, u_name):
        if not self.ara({"u_ID": {"$in": [str(u_ID), int(u_ID)]}}):
            return self.collection.insert_one(
                {
                    "u_ID": u_ID,
                    "u_usr": u_usr,
                    "u_name": u_name,
                }
            )
        else:
            return None

    def sil(self, u_ID):
        if not self.ara({"u_ID": {"$in": [str(u_ID), int(u_ID)]}}):
            return None

        self.collection.delete_one({"u_ID": {"$in": [str(u_ID), int(u_ID)]}})
        return True

    @property
    def user_ids(self):
        return list(self.ara({"u_ID": {"$exists": True}}).keys())


async def log_send(event):
    j = await event.client(GetFullUserRequest(event.chat_id))
    u_ID = j.user.id
    u_usr = f"@{j.user.username}" if j.user.username else None
    u_name = f"{j.user.first_name or ''} {j.user.last_name or ''}".strip()
    komut = event.text

    # Kullanıcı Kaydet
    db = pinterest_db()
    db.ekle(u_ID, u_usr, u_name)


# to check the total numbers of bot users (OWNER cmd)
@bot.on(events.NewMessage(pattern="/stats"))
async def say(event):
    j = await event.client(GetFullUserRequest(event.chat_id))

    db = pinterest_db()
    db.ekle(j.user.id, j.user.username, j.user.first_name)

    def USERS():
        return db.user_ids

    await event.client.send_message(
        OWNER, f"» ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛs ᴏғ ᴘɪɴᴛᴇʀᴇsᴛ ᴅʟ ᴘʀᴏ ʙᴏᴛ : \n\n **{len(USERS())}** ᴜsᴇʀs"
    )

@bot.on(events.NewMessage(pattern="/start", func=lambda e: e.is_private))
async def start(event):
    await log_send(event)
    j = await event.client(GetFullUserRequest(event.chat_id))
    dm = f"➻ ᴜsᴇʀ [{j.user.first_name}](tg://user?id={event.chat_id})\n➻ ɪɴᴘᴜᴛs: {event.message.message}"
    await bot.send_message(OWNER, dm)
    if event:
        markup = bot.build_reply_markup(
            [
                [
                    Button.url(text="✨sᴜᴘᴘᴏʀᴛ✨", url=SUPPORT_CHAT),
                    Button.url(text="🥀ᴅᴇᴠᴇʟᴏᴘᴇʀ🥀", url="ALPHA099.t.me"),
                ],
                [Button.inline(text="➻ σтнєя вσтѕ", data="otherbots")],
            ]
        )
        await bot.send_message(event.chat_id, msg, buttons=markup, link_preview=False)


@bot.on(events.NewMessage(pattern="/vid ?(.*)", func=lambda e: e.is_private))
async def vid(event):
    await log_send(event)
    try:
        j = await event.client(GetFullUserRequest(event.chat_id))
        dm = f"» ᴜsᴇʀ [{j.user.first_name}](tg://user?id={event.chat_id})\n» ᴜsᴇʀɪᴅ: {event.chat_id} \n» ʟɪɴᴋ: {event.message.message}"
        await bot.send_message(LOG_GROUP_ID, dm)
        markup = bot.build_reply_markup(
            [
                [
                    Button.url(text="✨sᴜᴘᴘᴏʀᴛ✨", url=SUPPORT_CHAT),
                    Button.url(text="🥀ᴅᴇᴠᴇʟᴏᴘᴇʀ🥀", url="ALPHA099.t.me"),
                ],
            ]
        )

        url = event.pattern_match.group(1)
        if url:
            x = await event.reply("`ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ʙᴀʙʏ...!!`\n\n**ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀᴛʟᴇᴀsᴛ 𝟹𝟶 sᴇᴄᴏɴᴅs ᴛᴏ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ᴏᴜᴛᴘᴜᴛ.**")

            # get_url = get_download_url(url)
            pin_dl = importlib.import_module("pin")
            pin_dl.run_library_main(
                url,
                TMP_DOWNLOAD_DIRECTORY,
                0,
                -1,
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                False,
                None,
                None,
                None,
            )
            j = None
            for file in os.listdir(TMP_DOWNLOAD_DIRECTORY):
                if file.endswith(".log"):
                    os.remove(f"{TMP_DOWNLOAD_DIRECTORY}/{file}")
                    continue
                if file.endswith(".mp4"):
                    j = TMP_DOWNLOAD_DIRECTORY + file

            # j = download_video(get_url)
            thumb_image_path = TMP_DOWNLOAD_DIRECTORY + "thumb_image.jpg"

            if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
                os.makedirs(TMP_DOWNLOAD_DIRECTORY)

            metadata = extractMetadata(createParser(j))
            duration = 0

            if metadata.has("duration"):
                duration = metadata.get("duration").seconds
                width = 0
                height = 0
                thumb = None

            if os.path.exists(thumb_image_path):
                thumb = thumb_image_path
            else:
                thumb = await take_screen_shot(
                    j, os.path.dirname(os.path.abspath(j)), (duration / 2)
                )
            width = 0
            height = 0
            if os.path.exists(thumb_image_path):
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
            c_time = time.time()
            await event.client.send_file(
                event.chat_id,
                j,
                thumb=thumb,
                caption="♡︎ тнαик уσυ fσя υѕιиg мє. \n\n» ᴀ ᴘɪɴᴛᴇʀᴇsᴛ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ ʙʏ [ɴᴏᴏʙ ʜᴇᴀᴠᴇɴ](https://NOOBHEAVEN.t.me)",
                force_document=False,
                allow_cache=False,
                reply_to=event.message.id,
                buttons=markup,
                attributes=[
                    DocumentAttributeVideo(
                        duration=duration,
                        w=width,
                        h=height,
                        round_message=False,
                        supports_streaming=True,
                    )
                ],
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, event, c_time, "loading...")
                ),
            )
            await event.delete()
            await x.delete()
            os.remove(j)
            os.remove(thumb_image_path)
        else:
            await event.reply(
                "**๏ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ʟɪɴᴋ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.**\n\n/img `PinterestURL` ғᴏʀ ɪᴍᴀɢᴇ\n/vid `PinterestURL` ғᴏʀ ᴠɪᴅᴇᴏ"
            )
    except FileNotFoundError:
        return


@bot.on(events.NewMessage(pattern="/img ?(.*)", func=lambda e: e.is_private))
async def img(event):
    await log_send(event)
    j = await event.client(GetFullUserRequest(event.chat_id))
    dm = f"» ᴜsᴇʀ [{j.user.first_name}](tg://user?id={event.chat_id})\n» ᴜsᴇʀɪᴅ: {event.chat_id} \n» ʟɪɴᴋ: {event.message.message}"
    await bot.send_message(OWNER, dm)
    markup = bot.build_reply_markup(
        [
            [
                Button.url(text="✨sᴜᴘᴘᴏʀᴛ✨", url=SUPPORT_CHAT),
                Button.url(text="🥀ᴅᴇᴠᴇʟᴏᴘᴇʀ🥀", url="ALPHA099.t.me"),
            ],
        ]
    )
    url = event.pattern_match.group(1)
    if url:
        x = await event.reply(
            "`ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ʙᴀʙʏ...!!`\n\n**ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ᴀᴛʟᴇᴀsᴛ 𝟹𝟶 sᴇᴄᴏɴᴅs ᴛᴏ ʀᴇᴄᴇɪᴠᴇ ᴛʜᴇ ᴏᴜᴛᴘᴜᴛ.**"
        )
        # get_url = await get_download_url(url)
        # j = await download_image(get_url)
        pin_dl = importlib.import_module("pin")
        pin_dl.run_library_main(
            url,
            TMP_DOWNLOAD_DIRECTORY,
            0,
            -1,
            False,
            False,
            False,
            False,
            False,
            True,
            False,
            False,
            None,
            None,
            None,
        )
        j = None
        for file in os.listdir(TMP_DOWNLOAD_DIRECTORY):
            if file.endswith(".log"):
                os.remove(f"{TMP_DOWNLOAD_DIRECTORY}/{file}")
                continue
            if file.endswith(".jpg"):
                j = TMP_DOWNLOAD_DIRECTORY + file

        if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
            os.makedirs(TMP_DOWNLOAD_DIRECTORY)
        c_time = time.time()
        await event.client.send_file(
            event.chat_id,
            j,
            caption="♡︎ тнαик уσυ fσя υѕιиg мє. \n\n» ᴀ ᴘɪɴᴛᴇʀᴇsᴛ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ ʙʏ [ɴᴏᴏʙ ʜᴇᴀᴠᴇɴ](https://NOOBHEAVEN.t.me)",
            force_document=False,
            allow_cache=False,
            reply_to=event.message.id,
            buttons=markup,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(d, t, event, c_time, "loading...")
            ),
        )
        await event.delete()
        await x.delete()
        os.remove(j)
    else:
        await event.reply(
            "๏ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ʟɪɴᴋ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.**\n\n/img `PinterestURL` ғᴏʀ ɪᴍᴀɢᴇ\n/vid `PinterestURL` ғᴏʀ ᴠɪᴅᴇᴏ"
        )


@bot.on(events.CallbackQuery(pattern=b"otherbots"))
async def otherbots(event):
    markup = bot.build_reply_markup(
        [
            [
                Button.url(text="✨sᴜᴘᴘᴏʀᴛ✨", url=SUPPORT_CHAT),
                Button.url(text="🥀ᴅᴇᴠᴇʟᴏᴘᴇʀ🥀", url="ALPHA099.t.me"),
            ],
            [Button.inline(text="ʙᴀᴄᴋ", data="home")],
        ]
    )
    await event.edit(
        "**➻ σтнєя вσтѕ:**\n\n"
        + "๏ [˹ᴛᴏxɪᴄ ✘ ᴍᴜsɪx˼ ♪](t.me/ToxicMuSixBot)\n"
        + "๏ [String Generator](t.me/StringMakerBot)\n"
        + "[✭ ᴍᴏʀᴇ ʙᴏᴛs ᴄᴏᴍɪɴɢ sᴏᴏɴ](t.me/ChatHuB_x_D)\n",
        buttons=markup,
        link_preview=False,
    )


@bot.on(events.CallbackQuery(pattern=b"home"))
async def home(event):
    markup = bot.build_reply_markup(
        [
            [
                Button.url(text="✨sᴜᴘᴘᴏʀᴛ✨", url=SUPPORT_CHAT),
                Button.url(text="🥀ᴅᴇᴠᴇʟᴏᴘᴇʀ🥀", url="ALPHA099.t.me"),
            ],
            [Button.inline(text="➻ σтнєя вσтѕ", data="otherbots")],
        ]
    )
    await event.edit(msg, buttons=markup, link_preview=False)


async def run_command(command: List[str]):
    process = await asyncio.create_subprocess_exec(
        *command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response: str = stderr.decode().strip()
    t_response: str = stdout.decode().strip()
    print(e_response)
    print(t_response)
    return t_response, e_response


async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name,
    ]
    # width = "90"
    t_response, e_response = await run_command(file_genertor_command)
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    logger.info(e_response)
    logger.info(t_response)
    return None


def humanbytes(size):
    """Input size in bytes,
    outputs in a human readable format"""
    # https://stackoverflow.com/a/49361727/4723940
    if not size:
        return ""
    # 2 ** 10 = 1024
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def time_formatter(seconds: int) -> str:
    """Inputs time in seconds, to get beautified time,
    as string"""
    result = ""
    v_m = 0
    remainder = seconds
    r_ange_s = {"days": 24 * 60 * 60, "hours": 60**2, "minutes": 60, "seconds": 1}
    for age, divisor in r_ange_s.items():
        v_m, remainder = divmod(remainder, divisor)
        v_m = int(v_m)
        if v_m != 0:
            result += f" {v_m} {age} "
    return result


async def progress(current, total, event, start, type_of_ps):
    """Generic progress_callback for both
    upload.py and download.py"""
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        elapsed_time = round(diff)
        if elapsed_time == 0:
            return
        speed = current / diff
        time_to_completion = round((total - current) / speed)
        estimated_total_time = elapsed_time + time_to_completion
        progress_str = "[{0}{1}]\nPercent: {2}%\n".format(
            "".join(["█" for _ in range(math.floor(percentage / 5))]),
            "".join(["░" for _ in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )
        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(total), time_formatter(estimated_total_time)
        )
        await event.edit("{}\n {}".format(type_of_ps, tmp))


bot.start()
bot.run_until_disconnected()