import asyncio
import base64
import random
import sys
import traceback

from pyrogram import Client, filters, idle
from pyrogram.errors import (ChatAdminRequired, FloodPremiumWait, FloodWait,
                             InputUserDeactivated, PeerIdInvalid,
                             SessionExpired, SessionRevoked, UserIsBlocked,
                             UserNotParticipant)
from pyrogram.types import (CallbackQuery, ChatJoinRequest,
                            InlineKeyboardButton, InlineKeyboardMarkup,
                            Message)

import config
from database import (add_accept_delay, add_group, add_user, all_groups,
                      all_users, already_dbg, get_adelay, get_all_peers,
                      remove_user)

owner = config.OWNER_ID
app = Client("Auto Approve Bot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
userApp = False
if config.SESSION:
    userApp = Client(
        "USER",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=config.SESSION
    )


print(f"Staring {app.name}")
app.start()
try:
    owner = app.get_users(config.OWNER_ID)
except PeerIdInvalid:
    print(f"Please start the @{app.me.username} first with {config.OWNER_ID} this id")
    sys.exit(1)
print(f"Owner: {('@'+owner.username) if owner.username else owner.id}")
print(f"Started {app.name} on @{app.me.username}")
if userApp:
    print("Starting user bot")
    userApp.start()
    print(f"Started user bot ont {('@'+userApp.me.username) if userApp.me.username else userApp.me.id}")
print("Started bot(s) now u can use me")


welcome=[
    "https://envs.sh/sMP.mp4",
    "https://envs.sh/sMb.mp4",
    "https://envs.sh/sMe.mp4",
    "https://envs.sh/sMi.mp4",
]

def_delay = config.DELAY


async def encode_decode(string, to_do="encode"):
    """
    Function to encode or decode strings.
    string: string to be decoded or encoded.
    to_do: 'encode' to encode the string, 'decode' to decode the string.
    """
    string = str(string)
    if to_do.lower() == "encode":
        encodee = string.encode("ascii")
        base64_ = base64.b64encode(encodee)
        B64 = base64_.decode("ascii")

    elif to_do.lower() == "decode":
        decodee = string.encode("ascii")
        base64_ = base64.b64decode(decodee)
        B64 = base64_.decode("ascii")

    return B64

async def create_approve_task(app: Client, j: ChatJoinRequest, after_delay: int):
    await asyncio.sleep(after_delay)
    chat = j.chat
    user = j.from_user
    if link := links.get(chat.id):
        link = link
    elif chat.username:
        link = f"t.me/{chat.username}"
    else:
        link = await chat.export_invite_link()
    id_ = app.me.id - user.id
    val = await encode_decode(f"{chat.id}_{id_}")
    start_link = f"tg://resolve?domain={app.me.username}&start={val}"
    kb = [
        [
            InlineKeyboardButton(f"{chat.title}", url=link)
        ],
        # [
        #     InlineKeyboardButton("Click here to join", url=start_link)
        # ]
    ]
    
    gif = random.choice(welcome)
    approved = False
    msg_sent = False
    try:
        approved = await j.approve()
        await app.send_animation(chat_id=user.id, animation=gif, caption=f"Hey There {user.first_name}\nYou join request to join {chat.title} has been accepted", reply_markup=InlineKeyboardMarkup(kb))
        msg_sent = True
    except Exception as e:
        print(traceback.format_exc())
        pass
        
    
    if not userApp:
        if not approved:
            print(f"Failed to approve join request of {user.id}")
        if not msg_sent:
            print(f"Failed to send message to this user")
        return
    
    if not approved:
        try:
            await userApp.approve_chat_join_request(chat.id, user.id)
        except:
            print(f"Failed to approve join request of {user.id}")
    if not msg_sent and userApp:
        try:
            await userApp.send_animation(chat_id=user.id, animation=gif, caption=f"Hey There {user.mention}\nYour join request to join the {chat.title} chat has been accepted", reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            print(traceback.format_exc())
            print("Got an error while trying to send message to user for create join request")
            print(e)
    
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

    
links = {

}

#pvtstart
@app.on_message(filters.command("start") & filters.private)
async def start(app: Client, msg: Message):
    add_user(msg.from_user.id)
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
    # print(msg.text.strip().split())
    global links
    if len(msg.text.strip().split()) > 1:
        arg = msg.text.split(None, 1)[1]
        # print(arg)
        if arg.startswith("j_"):
            channel = int(arg.split("_",1)[-1])
            if link := links.get(channel):
                link = link
            else:
                link = (await app.create_chat_invite_link(int(channel), creates_join_request=True)).invite_link
                links[channel] = link
            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Join channel", url = link)
                    ]
                ]
            )
            await msg.reply_photo(config.START_PIC, caption=f"Hey {msg.from_user.mention}! Thanks for verifying your are user\nClick on below button to join the channel", reply_markup=kb)
            return
        arg = await encode_decode(arg, "decode")
        channel, user = arg.split("_")
        channel = int(channel)
        user = int(user) + msg.from_user.id
        if user == app.me.id:
            chat = await app.get_chat(channel)
            if chat.username:
                link = f"t.me/{chat.username}"
            else:
                link = await chat.export_invite_link()
            kb = [
                [
                    InlineKeyboardButton(f"{chat.title}", url=link)
                ]
            ]
            approved = False
            try:
                approved = await app.approve_chat_join_request(channel, msg.from_user.id)
                await msg.reply_text("Your join reqest is accepted successfully",reply_markup=InlineKeyboardMarkup(kb))
            except:
                pass
            if not approved and userApp:
                try:
                    approved = await userApp.approve_chat_join_request(channel, user)
                    await msg.reply_text("Your join reqest is accepted successfully", reply_markup=InlineKeyboardMarkup(kb))
                except:
                    print(traceback.format_exc())
            if not approved:
                await msg.reply_text("Your join request will be accepted later")
            return

    await msg.reply_photo(
        photo=config.START_PIC,
        caption=f"Hᴇʟʟᴏ {msg.from_user.mention}💞,\n\n☉ Tʜɪs ɪs {app.me.mention},\n\n➲ A ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ᴍᴀᴅᴇ ғᴏʀ ᴀᴜᴛᴏ ᴀᴘᴘʀᴏᴠɪɴɢ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ɪɴ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\n➲ Jᴜsᴛ ᴀᴅᴅ {app.me.mention} ɪɴ ɢʀᴏᴜᴘs/ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴍᴀᴋᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴠɪᴀ ʟɪɴᴋ ʀɪɢʜᴛs.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"ᴀᴅᴅ {app.me.first_name}", url=f"https://t.me/{app.me.username}?startgroup=true")
                ]
            ]
        )
    )
    
    

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


async def client_resolve(user, retried=False):
    try:
        user = await app.get_users(user)
        if not user.is_deleted:
            return user.username if user.username else user.id
    except PeerIdInvalid:
        if userApp:
            try:
                user = await userApp.get_users(user)
                if not user.is_deleted:
                    return user.username if user.username else user.id
            except PeerIdInvalid:
                if retried:
                    return user
                try:
                    resolved = await userApp.resolve_peer(user)
                    return await client_resolve(resolved.user_id, True)
                except:
                    return user
        else:
            if retried:
                return user
            try:
                resolved = await app.resolve_peer(user)
                return await client_resolve(resolved.user_id, True)
            except:
                return user

#Boradcast creator
async def broadcaster(c: Client, chat_id: int, _id: int, media_grp=False):
    allusers = get_all_peers()
    global userApp
    global owner
    success = 0
    failed = 0
    deactivated = 0
    blocked = 0
    # if userApp:
    #     c = userApp
    #     try:
    #         if isinstance(owner, int):
    #             owner = await app.get_users(config.OWNER_ID)
    #         username = owner.username if owner.username else owner.id
    #         await c.send_message(username, "Using userbot to send messages")
    #     except (SessionExpired, SessionRevoked):
    #         print("Userbot session expired")
    #         c = app
    #     except:
    #         print(traceback.format_exc())
    #         pass
    for user in allusers:
        user = await client_resolve(user)
        try:
            if media_grp:
                await c.forward_media_group(chat_id=user, from_chat_id=chat_id, message_id=_id, hide_sender_name=True)
                success += 1
            else:
                await c.forward_messages(chat_id=user, from_chat_id=chat_id, message_ids=_id, hide_sender_name=True)
                success +=1
        except (FloodWait, FloodPremiumWait) as ex:
            await asyncio.sleep(ex.value)
            try:
                if media_grp:
                    await c.forward_media_group(chat_id=user, from_chat_id=chat_id, message_id=_id, hide_sender_name=True)
                    success += 1
                else:
                    await c.forward_messages(chat_id=user, from_chat_id=chat_id, message_ids=_id, hide_sender_name=True)
                    success +=1
            except PeerIdInvalid:
                try:
                    resolved = await c.resolve_peer(user)
                    user = resolved.user_id
                    if media_grp:
                        await c.forward_media_group(chat_id=user, from_chat_id=chat_id, message_id=_id, hide_sender_name=True)
                        success += 1
                    else:
                        await c.forward_messages(chat_id=user, from_chat_id=chat_id, message_ids=_id, hide_sender_name=True)
                        success +=1
                except (SessionExpired, SessionRevoked):
                    c = app
                    userApp = False
                    print("Userbot session expired")
                    allusers.append(user)
                except Exception as e:
                    print(f"Error while broadcast {e}")
                    print(traceback.format_exc())
                    continue
            except Exception as e:
                print(f"Error while broadcast {e}")
                print(traceback.format_exc())
                continue
        except InputUserDeactivated:
            deactivated +=1
            remove_user(user)
        except UserIsBlocked:
            blocked +=1
        except PeerIdInvalid:
            try:
                resolved = await c.resolve_peer(user)
                user = resolved.user_id
                if media_grp:
                    await c.forward_media_group(chat_id=user, from_chat_id=chat_id, message_id=_id, hide_sender_name=True)
                    success += 1
                else:
                    await c.forward_messages(chat_id=user, from_chat_id=chat_id, message_ids=_id, hide_sender_name=True)
                    success +=1
            except Exception as e:
                print(f"Error while broadcast {e}")
                print(traceback.format_exc())
                continue
        except (SessionExpired, SessionRevoked):
            c = app
            userApp = False
            print("Userbot session expired")
            allusers.append(user)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
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

@app.on_message(filters.command("acceptall") & filters.user(config.OWNER_ID))
async def accept_all_pending(_, m: Message):
    if not userApp:
        await m.reply_text("Please configure your session to use the command")
        return
    try:
        c_id = int(m.command[1])
    except ValueError:
        await m.reply_text("Channel id should be integer")
        return
    except IndexError:
        await m.reply_text("Please provide me channel id")
        return

    to_edit = await m.reply_text("Accepting all the pending join request")
    try:
        accepted = await userApp.approve_all_chat_join_requests(c_id)
        if accepted:
            await to_edit.edit_text("Approved all the pending request in the channel")
            return
        to_edit.edit_text("Failed to approve join requests")
    except Exception as e:
        await to_edit.edit_text(f"Make sure {userApp.me.mention} is admin in the provided channel\nError: {e}")
        print(traceback.format_exc())


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
    

idle()
#run
# async def main():
# print(f"Starting")
# try:
#     asyncio.run(main())
# except:
#     traceback.print_exc()
