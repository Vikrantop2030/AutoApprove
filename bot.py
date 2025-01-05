import asyncio
import random
import traceback

from pyrogram import Client, filters
from pyrogram.errors import (ChatAdminRequired, FloodWait,
                             InputUserDeactivated, PeerIdInvalid,
                             UserIsBlocked, UserNotParticipant)
from pyrogram.types import (CallbackQuery, ChatJoinRequest,
                            InlineKeyboardButton, InlineKeyboardMarkup,
                            Message)

import config
from database import (add_accept_delay, add_group, add_user, all_groups,
                      all_users, already_dbg, get_adelay, get_all_peers,
                      remove_user)

app = Client("Auto Approve Bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

welcome=[
    "https://telegra.ph/file/51d04427815840250d03a.mp4",
    "https://telegra.ph/file/f41fddb95dceca7b09cbc.mp4",
    "https://telegra.ph/file/a66716c98fa50b2edd63d.mp4",
    "https://telegra.ph/file/17a8ab5b8eeb0b898d575.mp4",
]

def_delay = config.DELAY

async def create_approve_task(app: Client, j: ChatJoinRequest, after_delay: int):
    await asyncio.sleep(after_delay)
    chat = j.chat
    user = j.from_user
    try:
        await j.approve()
        gif = random.choice(welcome)
        await app.send_animation(chat_id=user.id, animation=gif, caption=f"Hey There {user.first_name}\nWelcome To {chat.title}\n\n{user.first_name} Your Request To Join {chat.title} Has Been Accepted By {app.me.first_name}")
    except (UserIsBlocked, PeerIdInvalid):
        pass

    return


#approve 
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

    

#pvtstart
@app.on_message(filters.command("start") & filters.private)
async def start(app: Client, msg: Message):
    # if False:
    #     try:
    #         await app.get_chat_member(chat_id=config.CHANNEL, user_id=msg.from_user.id)
    #         add_user(msg.from_user.id)
    #         await msg.reply_photo(photo="https://telegra.ph/file/f394c45e5f2f147a37090.jpg", caption=f"Hᴇʟʟᴏ {msg.from_user.mention}💞,\n\n☉︎ Tʜɪs ɪs {app.me.mention},\n\n➲ A ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ɪɴ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\n➲ Jᴜsᴛ ᴀᴅᴅ {app.me.mention} ɪɴ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴍᴀᴋᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ʀɪɢʜᴛs..",
    #                              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"ᴀᴅᴅ {app.me.first_name}", url=f"https://t.me/{app.me.username}?startgroup=true")], [InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{config.CHANNEL}")]]))
    #     except UserNotParticipant:
    #         await msg.reply_text(text=f"To Use {app.me.mention}, You Must Subscribe To {(await app.get_chat(config.CHANNEL)).title}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join", url=f"https://t.me/{config.CHANNEL}")], [InlineKeyboardButton ("Joined ✅", url=f"https://t.me/{app.me.username}?start=start")]]))
    #     except ChatAdminRequired:
    #         await app.send_message(text=f"I'm not admin in fsub chat, Ending fsub...", chat_id=config.OWNER_ID)
    # else:
    # add_user(msg.from_user.id)
    await msg.reply_photo(
        photo="https://telegra.ph/file/f394c45e5f2f147a37090.jpg",
        caption=f"Hᴇʟʟᴏ {msg.from_user.mention}💞,\n\n☉ Tʜɪs ɪs {app.me.mention},\n\n➲ A ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ɪɴ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\n➲ Jᴜsᴛ ᴀᴅᴅ {app.me.mention} ɪɴ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴍᴀᴋᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ʀɪɢʜᴛs.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"ᴀᴅᴅ {app.me.first_name}", url=f"https://t.me/{app.me.username}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f"https://gojo_bots_network.t.me/")
                ],
            ]
        )
    )
    add_user(msg.from_user.id)
    

#Gcstart and id
@app.on_message(filters.command("start") & filters.group)
async def gc(app: Client, msg: Message):
    add_group(msg.chat.id)
    if msg.from_user:
        add_user(msg.from_user.id)
    await msg.reply_text(text=f"{msg.from_user.mention} Start Me In Private For More Info..", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start Me In Private", url=f"https://t.me/{app.me.username}?start=start")]]))

#stats
@app.on_message(filters.command("stats") & filters.user(config.OWNER_ID))
async def dbtool(app: Client, m: Message):
    xx = all_users()
    x = all_groups()
    await m.reply_text(text=f"Stats for {app.me.mention}\n🙋‍♂️ Users : {xx}\n👥 Groups : {x}")


#Boradcast creator
async def broadcaster(c: Client, chat_id: int, _id: int, media_grp=False):
    allusers = get_all_peers()
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    for user in allusers:
        try:
            if media_grp:
                await c.forward_media_group(user, chat_id, _id, hide_sender_name=True)
                success += 1
            else:
                await c.forward_messages(user, chat_id, _id, hide_sender_name=True)
                success +=1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            try:
                if media_grp:
                    await c.forward_media_group(user, chat_id, _id, hide_sender_name=True)
                    success += 1
                else:
                    await c.forward_messages(user, chat_id, _id, hide_sender_name=True)
                    success +=1
            except Exception as e:
                print(f"Error while broadcast {e}")
                continue
        except InputUserDeactivated:
            deactivated +=1
            remove_user(user)
        except UserIsBlocked:
            blocked +=1
        except Exception as e:
            print(e)
            failed +=1

    return success, failed, deactivated, blocked


#Broadcast
@app.on_message(filters.command("fbroadcast") & filters.user(config.OWNER_ID))
async def fcast(c: Client, m : Message):
    lel = await m.reply_text("`⚡️ Processing...`")
    success = 0
    failed = 0
    deactivated = 0
    repl_to = m.reply_to_message
    blocked = 0
    if not repl_to:
        await lel.edit_text("Please reply to a message")
        return
    _id = repl_to.id
    chat_id = m.chat.id
    is_grp = False
    if repl_to.media_group_id:
        is_grp = True
    
    success, failed, deactivated, blocked = await broadcaster(c, chat_id, _id, is_grp)

    await lel.edit(f"✅Successful Broadcast to {success} users.\n❌ Failed to {failed} users.\n👾 Found {blocked} Blocked users \n👻 Found {deactivated} Deactivated users.")
    
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


media_grps = []

async def removee(grp_id):
    await asyncio.sleep(300)
    try:
        media_grps.remove(grp_id)
    except:
        pass

    return


@app.on_message(filters.chat(config.CHANNEL_ID))
async def listen_and_broadcast(c: Client, m: Message):
    if m.media_group_id:
        if m.media_group_id in media_grps:
            return
        else:
            txt = f"grp:{m.id}"
            media_grps.append(m.media_group_id)
            asyncio.create_task(removee(m.media_group_id))

    else:
        txt = f"sol:{m.id}"
    
    kb = [
        [
            InlineKeyboardButton("Yes, broadcast", txt)
        ],
        [
            InlineKeyboardButton("No, don't broadcast", "delete")
        ]
    ]

    await c.send_message(config.OWNER_ID, "Hi there do you want to broadcast this message?", reply_markup=InlineKeyboardMarkup(kb), reply_to_chat_id=m.chat.id, reply_to_message_id=m.id)

@app.on_callback_query()
async def callbackss(c: Client, q: CallbackQuery):
    if q.data == "delete":
        await q.edit_message_text("Okay will not broadcast this message")
        return

    else:
        is_grp, id_ = q.data.split(":")
        is_grp = False if is_grp == "sol" else True
        
    success, failed, deactivated, blocked = await broadcaster(c, config.CHANNEL_ID, int(id_), is_grp)
    to_edit = await q.edit_message_text("Broadcasting this message")
    await to_edit.edit_text(f"✅Successful Broadcast to {success} users.\n❌ Failed to {failed} users.\n👾 Found {blocked} Blocked users \n👻 Found {deactivated} Deactivated users.")
    return
    


#run
print(f"Starting {app.name}")
try:
    app.run()
    print("Startd the bot")
except:
    traceback.print_exc()
