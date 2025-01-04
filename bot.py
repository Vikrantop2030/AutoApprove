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
            # Check if message is a media group (like a GIF or other media group)
            if repl_to.media:
                if repl_to.media_group_id:
                    # Send media group to users
                    await c.send_media_group(user, media=repl_to.media_group)
                    success += 1
                else:
                    # For single media, send directly (GIF, video, etc.)
                    if repl_to.video:
                        await c.send_video(user, video=repl_to.video, caption=repl_to.caption)
                    elif repl_to.animation:
                        await c.send_animation(user, animation=repl_to.animation, caption=repl_to.caption)
                    else:
                        await c.send_message(user, text=repl_to.text or repl_to.caption)
                    success += 1
            else:
                # Handle the case where it's a text message or empty media
                await c.send_message(user, text=repl_to.text or repl_to.caption)
                success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            try:
                if repl_to.media_group_id:
                    await c.send_media_group(user, media=repl_to.media_group)
                    success += 1
                else:
                    await c.send_message(user, text=repl_to.text or repl_to.caption)
                    success += 1
            except Exception as e:
                print(f"Error while broadcasting: {e}")
                continue
        except InputUserDeactivated:
            deactivated += 1
            remove_user(user)
        except UserIsBlocked:
            blocked += 1
        except PeerIdInvalid:
            # Skip users with invalid peer IDs
            continue
        except Exception as e:
            print(f"Unexpected error while broadcasting: {e}")
            failed += 1

    await lel.edit(f"✅ Successful Broadcast to {success} users.\n❌ Failed to {failed} users.\n👾 Found {blocked} Blocked users \n👻 Found {deactivated} Deactivated users.")
