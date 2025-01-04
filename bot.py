import asyncio
import random
import traceback
import re

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
    "https://i.ibb.co/09BvZdc/ezgif-com-video-to-gif-converter.gif",  # Updated welcome image
]

def_delay = config.DELAY

async def create_approve_task(app: Client, j: ChatJoinRequest, after_delay: int):
    await asyncio.sleep(after_delay)
    chat = j.chat
    user = j.from_user
    try:
        await j.approve()
        gif = random.choice(welcome)
        
        # Generate the inline button with the channel preview
        join_button = InlineKeyboardButton("Click to View Channel", url=f"https://t.me/{chat.username}") if chat.username else None
        
        # If the channel is private, show the invite link instead with the "Join" button
        if not join_button:
            invite_link = await app.export_chat_invite_link(chat.id)  # Private channel invite link
            join_button = InlineKeyboardButton("Click to View Channel", url=invite_link)
        
        # Send the welcome message with the preview and inline button
        await app.send_animation(
            chat_id=user.id, 
            animation=gif, 
            caption=f"Hey There {user.first_name}\nWelcome To {chat.title}\n\n{user.first_name} Your Request To Join {chat.title} Has Been Accepted By {app.me.first_name}",
            reply_markup=InlineKeyboardMarkup([[join_button]]),
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
        photo="https://i.ibb.co/09BvZdc/ezgif-com-video-to-gif-converter.gif",  # Updated welcome image
        caption=f"Hᴇʟʟᴏ {msg.from_user.mention}💞,\n\n☉ Tʜɪs ɪs {app.me.mention},\n\n➲ A ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ɪɴ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\n➲ Jᴜsᴛ ᴀᴅᴅ {app.me.mention} ɪɴ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴍᴀᴋᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ʀɪɢʜᴛs.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"ᴀᴅᴅ {app.me.first_name}", url=f"https://t.me/{app.me.username}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f"https://gojo_bots_network.t.me/")  # Update to actual channel URL
                ],
            ]
        )
    )
    add_user(msg.from_user.id)

# Group start and id
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
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    repl_to = m.reply_to_message
    if not repl_to:
        await lel.edit_text("Please reply to a message")
        return

    _id = repl_to.id
    chat_id = m.chat.id
    for user in allusers:
        try:
            if repl_to.text:  # Check if there's text content
                print(f"Sending message to {user.id}: {repl_to.text}")
                await c.send_message(user, text=repl_to.text or repl_to.caption)
                success += 1
            elif repl_to.animation:  # Handle GIFs
                print(f"Sending GIF: {repl_to.animation.file_id}")
                await c.send_animation(user, animation=repl_to.animation)
                success += 1
            elif repl_to.photo:  # Handle images
                print(f"Sending Photo: {repl_to.photo.file_id}")
                await c.send_photo(user, photo=repl_to.photo)
                success += 1
            else:
                print(f"No valid content to send for user {user.id}.")
                failed += 1

        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            try:
                if repl_to.animation:
                    await c.send_animation(user, animation=repl_to.animation)
                    success += 1
                elif repl_to.photo:
                    await c.send_photo(user, photo=repl_to.photo)
                    success += 1
                else:
                    await c.send_message(user, text=repl_to.text or repl_to.caption)
                    success += 1
            except Exception as e:
                print(f"Error while broadcasting media {e}")
                continue
        except InputUserDeactivated:
            deactivated += 1
            remove_user(user)
        except UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"Error while broadcasting message: {e}")
            failed += 1

    await lel.edit(f"✅Successful Broadcast to {success} users.\n❌ Failed to {failed} users.\n👾 Found {blocked} Blocked users \n👻 Found {deactivated} Deactivated users.")

# Delay
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
