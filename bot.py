import asyncio
import random
import logging
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import UserIsBlocked, PeerIdInvalid, InputUserDeactivated, FloodWait

# Configurations
API_ID = config.API_ID  # Replace this with the actual integer value from your config file
API_HASH = config.API_HASH  # Replace this with the actual string value from your config file
BOT_TOKEN = config.BOT_TOKEN  # Replace this with the actual token from your config file
OWNER_ID = 123456789  # Replace this with your actual Telegram user ID
WELCOME_GIFS = [
    "https://i.ibb.co/MNH8176/logo.jpg",
    "https://i.ibb.co/MNH8176/logo.jpg",
    "https://i.ibb.co/MNH8176/logo.jpg"
]
DEFAULT_DELAY = config.DELAY  # Replace this with the default delay value from your config file

# Initialize Bot
app = Client("AutoApproveBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (replace with a proper database)
groups = {}
users = set()

# Helper Functions
def add_group(group_id: int):
    """Add a group to the tracked groups."""
    if group_id not in groups:
        groups[group_id] = DEFAULT_DELAY

def add_user(user_id: int):
    """Add a user to the tracked users."""
    users.add(user_id)

def set_delay(group_id: int, delay: int):
    """Set a custom delay for a group."""
    if group_id in groups:
        groups[group_id] = delay

def get_delay(group_id: int):
    """Get the delay for a group."""
    return groups.get(group_id, DEFAULT_DELAY)

# Bot Commands and Handlers
@app.on_chat_join_request()
async def auto_approve_request(client: Client, join_request: ChatJoinRequest):
    """Automatically approve join requests after a delay."""
    group_id = join_request.chat.id
    user = join_request.from_user
    delay = get_delay(group_id)

    logger.info(f"Received join request from {user.id} for group {group_id}. Delay: {delay}s")

    await asyncio.sleep(delay)

    try:
        await join_request.approve()
        gif = random.choice(WELCOME_GIFS)
        await client.send_animation(
            chat_id=user.id,
            animation=gif,
            caption=f"Welcome, {user.first_name}!\nYour request to join '{join_request.chat.title}' has been approved!"
        )
        logger.info(f"Approved {user.id}'s request for group {group_id}")
    except (UserIsBlocked, PeerIdInvalid):
        logger.warning(f"Failed to notify {user.id}")
    except Exception as e:
        logger.error(f"Error approving request for {user.id}: {e}")

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Handle the /start command in private chat."""
    add_user(message.from_user.id)
    await message.reply_photo(
        photo=random.choice(WELCOME_GIFS),
        caption="👋 Hello! I'm here to automatically approve join requests for your group or channel.\n\n"
                "➡️ Add me to a group or channel and make me an admin with invite permissions.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Add Me to a Group", url=f"https://t.me/{app.me.username}?startgroup=true")]
        ])
    )

@app.on_message(filters.command("setdelay") & filters.user(OWNER_ID))
async def set_delay_command(client: Client, message: Message):
    """Set the delay for auto-approving join requests."""
    try:
        _, group_id, delay = message.text.split()
        group_id = int(group_id)
        delay = int(delay)
        set_delay(group_id, delay)
        await message.reply(f"✅ Delay set to {delay} seconds for group ID {group_id}.")
    except ValueError:
        await message.reply("❌ Invalid command format. Use: /setdelay <group_id> <delay_in_seconds>")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_command(client: Client, message: Message):
    """Display bot statistics."""
    await message.reply(
        f"📊 **Bot Stats**:\n\n"
        f"👥 Groups: {len(groups)}\n"
        f"🙋‍♂️ Users: {len(users)}"
    )

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_command(client: Client, message: Message):
    """Broadcast a message to all users."""
    if not message.reply_to_message:
        await message.reply("❌ Reply to a message to broadcast it.")
        return

    broadcast_message = message.reply_to_message
    success, failed = 0, 0

    for user_id in users:
        try:
            await client.forward_messages(user_id, from_chat_id=broadcast_message.chat.id, message_ids=broadcast_message.id)
            success += 1
        except Exception as e:
            logger.warning(f"Failed to send message to {user_id}: {e}")
            failed += 1

    await message.reply(f"✅ Broadcast completed.\nSuccess: {success}\nFailed: {failed}")

# Run Bot
if __name__ == "__main__":
    logger.info("Bot is starting...")
    app.run()
