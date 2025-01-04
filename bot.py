import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import (ChatJoinRequest, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)
from pyrogram.errors import ChatAdminRequired, FloodWait, UserIsBlocked, PeerIdInvalid

import config
from database import (add_accept_delay, add_group, add_user, get_adelay, get_all_peers)

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
        
        # Check if the channel is public
        if chat.username:
            # Public channel link
            channel_link = f"https://t.me/{chat.username}"
            # Inline button for public channel
            buttons = [
                [InlineKeyboardButton("Join Channel", url=channel_link)]
            ]
            welcome_text = f"Hey {user.first_name}!\nWelcome to {chat.title}\n\nYour request to join {chat.title} has been accepted.\n\nClick below to join the channel:"
        else:
            # Private channel: Generate an invite link if the bot has permission
            try:
                link = await app.export_chat_invite_link(chat.id)
                channel_link = link
                # Display channel preview for private channel
                buttons = [
                    [InlineKeyboardButton("Join Channel", url=channel_link)]
                ]
                welcome_text = f"Hey {user.first_name}!\nWelcome to {chat.title}\n\nYour request to join {chat.title} has been accepted.\n\nClick below to join the private channel:"
            except ChatAdminRequired:
                # If the bot can't generate the invite link
                channel_link = "Private channel. Contact admin for an invite link."
                buttons = []
                welcome_text = f"Hey {user.first_name}!\nWelcome to {chat.title}\n\nYour request to join {chat.title} has been accepted.\n\n{channel_link}"

        # Send the welcome message with a GIF and inline button
        await app.send_animation(chat_id=user.id, animation=gif, caption=welcome_text, reply_markup=InlineKeyboardMarkup(buttons))
    except (UserIsBlocked, PeerIdInvalid):
        pass

    return


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


@app.on_message(filters.command("start") & filters.private)
async def start(app: Client, msg: Message):
    await msg.reply_photo(
        photo="https://telegra.ph/file/f394c45e5f2f147a37090.jpg",
        caption=f"Hello {msg.from_user.mention},\n\nI am an auto-approve bot that helps admins manage join requests.\nAdd me to your group and make me an admin to start using the bot.",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(f"Add {app.me.first_name}", url=f"https://t.me/{app.me.username}?startgroup=true")],
                [InlineKeyboardButton("Channel", url="https://yourchannel.link/")]
            ]
        )
    )

# Handle private group start
@app.on_message(filters.command("start") & filters.group)
async def gc(app: Client, msg: Message):
    add_group(msg.chat.id)
    if msg.from_user:
        add_user(msg.from_user.id)
    await msg.reply_text(text=f"{msg.from_user.mention}, Start me in private for more info..", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Start Me In Private", url=f"https://t.me/{app.me.username}?start=start")]]))

# Broadcast functionality and other commands (not included for brevity)

# Run the bot
print(f"Starting {app.name}")
app.run()
