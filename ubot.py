# ubot.py
from telethon import TelegramClient, events
from telethon.sessions import SQLiteSession
import requests
import qrcode
from io import BytesIO
import asyncio
import sys
import traceback
import os   # <-- WAJIB DITAMBAHKAN

# ============================
# CONFIG
# ============================
API_ID = 30553961
API_HASH = "ad4df502119a5d0d675f8bf8ea2dd020"
SESSION = "kuro_userbot"  # file sesi: kuro_userbot.session

OWNER_ID = 8113738409   # ID kamu sendiri
HTTP_TIMEOUT = 15       # Timeout API QRIS

# ============================
# QRIS HELPER
# ============================
def generate_qris(amount, qris_statis):

    try:
        amount_int = int(amount)
        if amount_int < 1000:
            return {"status": "error", "message": "Nominal minimal 1000"}
        amount = str(amount_int)
    except:
        return {"status": "error", "message": "Nominal tidak valid"}

    url = "https://api.qrisku.biz.id/"
    data = {
        "amount": amount,
        "qris_statis": qris_statis
    }

    try:
        resp = requests.post(url, json=data, timeout=HTTP_TIMEOUT)
    except Exception as e:
        return {"status": "error", "message": f"Request error: {str(e)}"}

    if not resp.ok:
        return {"status": "error", "message": f"HTTP {resp.status_code}: {resp.text}"}

    try:
        j = resp.json()
    except:
        return {"status": "error", "message": "Response bukan JSON: " + resp.text[:300]}

    # Format sukses normal
    if j.get("status") == "success" and j.get("qris_string"):
        return {"status": "success", "qris_string": j["qris_string"]}

    # Format embed “data”
    if isinstance(j.get("data"), dict) and j["data"].get("qris_string"):
        return {"status": "success", "qris_string": j["data"]["qris_string"]}

    # Fallback scan key
    for k in ("qris_string", "qris", "qr", "qrcode"):
        if isinstance(j.get(k), str) and len(j[k]) > 20:
            return {"status": "success", "qris_string": j[k]}

    return {"status": "error", "message": j.get("message", "Format JSON tidak dikenali")}


# ============================
# MAIN
# ============================
async def main():
    session_file = f"{SESSION}.session"
    session_exists = os.path.exists(session_file)

    client = TelegramClient(SESSION, API_ID, API_HASH)

    if session_exists:
        print("🔐 Session ditemukan, login tanpa OTP...")
        await client.connect()

        if not await client.is_user_authorized():
            print("⚠️ Session rusak. Login OTP dibutuhkan.")
            await client.start()

    else:
        print("📲 Session belum ada, login OTP...")
        await client.start()

    me = await client.get_me()
    my_id = me.id
    print(f"🔥 Userbot aktif sebagai: {me.first_name} ({my_id})")

    QRIS_STATIS = (
        "00020101021126570011ID.DANA.WWW011893600915324987796602092498779660303UMI51440014ID.CO.QRIS.WWW0215ID10254361150300303UMI5204481453033605802ID5910KaiiMarket6012Kab. Cilacap61055326563045535"
    )

# ============================
    # COMMAND .qr
    # ============================
    @client.on(events.NewMessage(pattern=r"^\.qr(?:\s+(\d+))?$"))
    async def qris_handler(event):
        try:
            if event.sender_id != OWNER_ID:
                return

            m = event.pattern_match
            if not m or not m.group(1):
                await event.reply("⚠️ Format: `.qr 5000`")
                return

            amount = m.group(1)
            await event.reply(f"🔄 Membuat QRIS Rp{int(amount):,}...")

            result = generate_qris(amount, QRIS_STATIS)

            if result["status"] != "success":
                await event.reply("❌ Gagal: " + result["message"])
                return

            qris_string = result["qris_string"]

            # Generate QR
            qr = qrcode.make(qris_string)
            buf = BytesIO()
            qr.save(buf, format="PNG")
            buf.seek(0)

            # FIX terpenting agar tidak unnamed
            buf.name = f"qris_{amount}.png"

            await client.send_file(
                event.chat_id,
                buf,
                caption=f"✅ QRIS Rp{int(amount):,}\nKirim bukti pembayaran.",
                force_document=False
            )

        except Exception:
            traceback.print_exc()
            await event.reply("❌ Error internal. Cek console.")

# ============================
    # COMMAND .m
    # ============================
    @client.on(events.NewMessage(pattern=r"^\.m$"))
    async def dana_masuk_handler(event):
        if event.sender_id != OWNER_ID:
            return

        teks = (
            "<blockquote>💳 𝗗𝗔𝗡𝗔 𝗠𝗔𝗦𝗨𝗞</blockquote>\n"
            "<blockquote>❌ 𝗔𝗟𝗟 𝗧𝗥𝗫 𝗡𝗢 𝗥𝗘𝗙𝗙 ‼️</blockquote>"
        )

        await event.reply(teks, parse_mode="html")

    # ============================
    # COMMAND .done
    # ============================
    @client.on(events.NewMessage(pattern=r"^\.done (.+)"))
    async def done_handler(event):
        if event.sender_id != OWNER_ID:
            return

        raw = event.pattern_match.group(1)

        try:
            barang, nominal, payment = [x.strip() for x in raw.split(",")]
        except:
            await event.reply(
                "⚠️ Format salah!\nContoh:\n`.done panel unlimited, 5000, DANA`"
            )
            return

        import datetime
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # TEMPLATE BLOCKQUOTE
        teks = (
    "<blockquote>「 𝗧𝗥𝗔𝗡𝗦𝗔𝗞𝗦𝗜 𝗕𝗘𝗥𝗛𝗔𝗦𝗜𝗟 」</blockquote>\n"
    "<blockquote>"
    f"📦 ʙᴀʀᴀɴɢ : {barang}\n"
    f"💸 ɴᴏᴍɪɴᴀʟ : {nominal}\n"
    f"🕰️ ᴡᴀ𝗸𝘁𝘂 : {waktu}\n"
    f"💳 ᴘᴀʏᴍᴇɴᴛ : {payment}"
    "</blockquote>\n"
    "<blockquote>𝚃𝚎𝚛𝚒𝚖𝚊𝗸𝗮𝘀𝗶𝗵 𝚝𝗲𝗹𝗮𝗵 𝚘𝗿𝗱𝗲𝗿</blockquote>"
)

        reply_msg = await event.get_reply_message()

        # REPLY GAMBAR → kirim gambar + caption
        if reply_msg and reply_msg.media:
            try:
                await client.send_file(
                    event.chat_id,
                    reply_msg.media,
                    caption=teks,
                    parse_mode="html"
                )
                return
            except:
                pass

        # TANPA REPLY GAMBAR → teks saja
        await event.reply(teks, parse_mode="html")
    
    # ============================
    # LOG PRIVATE CHAT SAJA
    # ============================
    @client.on(events.NewMessage(incoming=True))
    async def private_log(event):
        try:
            if event.sender_id == my_id:
                return

            chat = await event.get_chat()

            # Jika GRUP → SKIP
            if getattr(chat, "title", None):
                return

            sender = await event.get_sender()
            text = event.raw_text or "<non-text>"

            print(f"\n[PRIVATE] {sender.first_name} ({sender.id})\n{text}")

        except:
            traceback.print_exc()

    await client.run_until_disconnected()


# ============================
# RUN
# ============================
if __name__ == "__main__":
    asyncio.run(main())