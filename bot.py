import asyncio
import random
import traceback

from pyrogram import Client, filters
from pyrogram.errors import (ChatAdminRequired, FloodWait,
                             InputUserDeactivated, PeerIdInvalid,
                             UserIsBlocked, UserNotParticipant)
from pyrogram.types import (ChatJoinRequest, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

import config
from database import (add_accept_delay, add_group, add_user, all_groups,
                      all_users, already_dbg, get_adelay, get_all_peers,
                      remove_user)

app = Client("Auto Approve Bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

welcome = [
    "https://i.ibb.co/MNH8176/logo.jpg",
    "https://i.ibb.co/MNH8176/logo.jpg",
    "https://i.ibb.co/MNH8176/logo.jpg",
    "https://i.ibb.co/MNH8176/logo.jpg",
]

def_delay = config.DELAY

async def create_approve_task(app: Client, j: ChatJoinRequest, after_delay: int):
    await asyncio.sleep(after_delay)
    chat = j.chat
    user = j.from_user
    try:
        await j.approve()
        gif = random.choice(welcome)
        await app.send_animation(
            chat_id=user.id,
            animation=gif,
            caption=f"🎉 Hey {user.first_name}, welcome to {chat.title}! 🎉\n\nWe’re excited to have you join us here. Your request to join {chat.title} has been successfully approved by {app.me.first_name}. 😊\n\nFeel free to explore, engage with the community, and have fun! 🚀\n\nMake sure to check out our [Channel](https://t.me/{config.CHANNEL}) for updates and more."
        )
    except (UserIsBlocked, PeerIdInvalid):
        pass

    return


# Approve 
@app.on_chat_join_request()
async def approval(app: Client, m: ChatJoinRequest):
    usr = m.from_user
    cht = m.chat
    global def_delay
    Delay = get_adelay(cht.id)
    if not Delay:
        add_accept_delay(cht.id, def_delay)
        Delay = def_delay
    add_group(cht.id)
    add_user(usr.id)

    asyncio.create_task(create_approve_task(app, m, Delay))


# Private start
@app.on_message(filters.command("start") & filters.private)
async def start(app: Client, msg: Message):
    await msg.reply_photo(
        photo="https://i.ibb.co/MNH8176/logo.jpg",
        caption=f"Hᴇʟʟᴏ {msg.from_user.mention}💞,\n\n☉︎ Tʜɪs ɪs {app.me.mention},\n\n➲ A ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ɪɴ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\n➲ Jᴜsᴛ ᴀᴅᴅ {app.me.first_name} ɪɴ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴍᴀᴋᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ʀɪɢʜᴛs.\n\nFeel free to join our [Channel](https://t.me/{config.CHANNEL}) for more info.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"ᴀᴅᴅ {app.me.first_name}", url=f"https://t.me/{app.me.username}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{config.CHANNEL}")
                ],
            ]
        )
    )
    add_user(msg.from_user.id)


# Gcstart and id
@app.on_message(filters.command("start") & filters.group)
async def gc(app: Client, msg: Message):
    add_group(msg.chat.id)
    if msg.from_user:
        add_user(msg.from_user.id)
    await msg.reply_text(text=f"{msg.from_user.mention} Start Me In Private For More Info..", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start Me In Private", url=f"https://t.me/{app.me.username}?start=start")]]))

# Stats
@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def dbtool(app: Client, m: Message):
    xx = all_users()
    x = all_groups()
    await m.reply_text(text=f"Stats for {app.me.mention}\n🙋‍♂️ Users : {xx}\n👥 Groups : {x}")

# Broadcast
@app.on_message(filters.command("fbroadcast") & filters.user(config.OWNER_ID))
async def fcast(c: Client, m: Message):
    allusers = get_all_peers()
    lel = await m.reply_text("⚡️ Processing...")
    success, failed, deactivated, blocked = 0, 0, 0, 0

    # Check if there's a reply message, otherwise use the original message.
    if m.reply_to_message:
        broadcast_msg = m.reply_to_message  # Use the message being replied to.
    else:
        # Strip the command and take the rest of the text in the message
        broadcast_msg_text = m.text.split(" ", 1)[1] if len(m.text.split(" ", 1)) > 1 else None
        if broadcast_msg_text:
            broadcast_msg_text = broadcast_msg_text  # Use just the text after the command
        else:
            await lel.edit_text("❌ No message content found after the command.")
            return

    # Broadcast the message to all users
    for user in allusers:
        try:
            if broadcast_msg_text:
                # Send the stripped text message to user
                await c.send_message(
                    chat_id=user,
                    text=broadcast_msg_text,
                    parse_mode=None  # Temporarily disabled parse mode
                )
            else:
                failed += 1
                continue  # Skip users for unsupported media types.
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
        except InputUserDeactivated:
            deactivated += 1
            remove_user(user)
        except UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"Error for user {user}: {e}")
            failed += 1

    # After processing, update the user with the result
    await lel.edit_text(
        f"✅ Successfully broadcast to {success} users.\n"
        f"❌ Failed for {failed} users.\n"
        f"👾 Found {blocked} blocked users.\n"
        f"👻 Found {deactivated} deactivated users."
    )


@app.on_message(filters.command("delay") & filters.user(config.OWNER_ID))
async def add_delay_before_accepting(_, m: Message):
    splited = m.command
    if len(m.command) != 3:
        await m.reply_text("**USAGE**\n/delay [chat id] [delay in seconds]")
        return
    
    try:
        chat_id = int(splited[1])
        delay = int(splited[2])
    except:
        await m.reply_text("Chat id and delay should be integer")
        return
    
    if not already_dbg(chat_id):
        await m.reply_text("This chat id doesn't exist in my database")
        return
    
    timee = add_accept_delay(chat_id, delay)
    if timee:
        await m.reply_text(f"Updated delay from {timee} seconds to {delay} seconds")
        return
    
    await m.reply_text(f"Added delay of {delay} seconds before accepting join request")
    return


# Run
print(f"Starting {app.name}")
try:
    app.run()
    print("Started the bot")
except:
    traceback.print_exc()
