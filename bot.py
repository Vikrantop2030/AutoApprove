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
    "https://i.ibb.co/09BvZdc/ezgif-com-video-to-gif-converter.gif",
]

def_delay = config.DELAY

async def create_approve_task(app: Client, j: ChatJoinRequest, after_delay: int):
    await asyncio.sleep(after_delay)
    chat = j.chat
    user = j.from_user
    try:
        await j.approve()
        gif = random.choice(welcome)
        
        # Check if the channel is private and get the invite link if possible
        if chat.username:
            # If the channel is public, use the public link
            channel_link = f"https://t.me/{chat.username}"
        else:
            # If the channel is private, try to generate an invite link
            try:
                # Check if the bot has the necessary admin rights to generate an invite link
                link = await app.export_chat_invite_link(chat.id)
                channel_link = link
            except ChatAdminRequired:
                # If the bot doesn't have the necessary rights, notify the user
                channel_link = "Private channel, no invite link available. Please contact the admin."
            except Exception as e:
                # Handle any other errors
                channel_link = f"Error generating invite link: {str(e)}"

        await app.send_animation(chat_id=user.id, animation=gif, caption=f"Hey There {user.first_name}\nWelcome To {chat.title}\n\n{user.first_name} Your Request To Join {chat.title} Has Been Accepted By {app.me.first_name}\n\nJoin the channel: {channel_link}")
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
        photo="https://telegra.ph/file/f394c45e5f2f147a37090.jpg",
        caption=f"Hᴇʟʟᴏ {msg.from_user.mention}💞,\n\n☉ Tʜɪs ɪs {app.me.mention},\n\n➲ A ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ɪɴ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\n➲ Jᴜsᴛ ᴀᴅᴅ {app.me.mention} ɪɴ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴍᴀᴋᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ʀɪɢʜᴛs.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"ᴀᴅᴅ {app.me.first_name}", url=f"https://t.me/{app.me.username}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f"https://gojo_bots_network.t.me/"),
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
            if m.media_group_id:
                # Instead of forwarding the media, send the media as a message to the users
                await c.send_media_group(user, media=repl_to.media_group)
                success += 1
            else:
                # Send the message content directly
                await c.send_message(user, text=repl_to.text or repl_to.caption)
                success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            try:
                if m.media_group_id:
                    await c.send_media_group(user, media=repl_to.media_group)
                    success += 1
                else:
                    await c.send_message(user, text=repl_to.text or repl_to.caption)
                    success += 1
            except Exception as e:
                print(f"Error while broadcast {e}")
                continue
        except InputUserDeactivated:
            deactivated += 1
            remove_user(user)
        except UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(e)
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
