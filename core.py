import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import openai
import time
from cryptography.fernet import Fernet
from decouple import config

api_id = config('API_ID')
api_hash = config('API_HASH')
key = config('DECRYPTION_KEY')

chat_id = 752041694
# chat_id = 'ajxterry'
dev_chat_id = -1001768006261

cipher_suite = Fernet(key)

with open("encrypted_session_file.session", "rb") as file:
    encrypted_data = file.read()

decrypted_data = cipher_suite.decrypt(encrypted_data)

with open("me.session", "wb") as file:
    file.write(decrypted_data)


openai_key = config('OPENAI_API_KEY')

gpt_mode = False
messages = []


async def generate_ai_chat_response(msgs: list):
    global messages
    response = await openai.ChatCompletion.acreate(
        model="gpt-4",
        messages=msgs,
        stream=True
    )
    response_text = ''
    prev_time = time.time()

    async for r in response:
        response_text += r.choices[0].delta.get('content', '')
        delta = time.time() - prev_time
        if delta >= 2:
            prev_time = time.time()
            yield response_text + '...'

    messages.append(
        {'role': 'assistant',
         'content': response_text}
    )
    yield response_text


openai.api_key = openai_key


reactions = ['👍', '❤️', '🌚', '🔥', '👌', '😁', '🐳', '😢', '🤯', '🤔', '💩', '🗿', '😇', '😭', '❤️‍🔥', '💯',
             '👎', '🥰', '👏', '🤬', '🎉', '🤩', '🤮', '🙏', '🕊️', '🤡', '🥱', '🌭', '🥴', '😍', '🤣', '⚡️',
             '🍌', '🏆', '💔', '🤨', '😐', '🍓', '🍾', '💋', '🖕', '😈', '😴', '🤓', '👻', '👨‍💻', '👀', '🎃',
             '🙈', '😨', '🤝', '✍️', '🤗', '🫡', '🎅', '🎄', '☃️️', '💅', '🤪', '🆒', '💘', '🙊', '🙉', '🦄',
             '💊', '😎', '👾', '🤷‍♂️', '🤷', '🤷‍♀️', '😡']

# Initialize the Pyrogram client
app = Client("me", api_id=api_id, api_hash=api_hash)

# Define a message filter to only process messages in the specific chat and sent by you
f = (filters.chat(chat_id) | filters.chat(dev_chat_id))
her_message_filter = filters.chat(chat_id) & ~filters.user('lor3m')


# Create a handler to send a random reaction to messages in the specified chat
# @app.on_message(f)
# async def send_random_reaction(client, message):
#     reaction = random.choice(reactions)
#     await client.send_reaction(message.chat.id, message.id, reaction, big=True)


@app.on_message(her_message_filter & filters.text)
async def send_ai_chat_response(client, message):
    global gpt_mode
    global messages

    messages.append({
        'role': 'user',
        'content': message.text
    })

    if gpt_mode:
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        message = await message.reply_text('...')
        async for response in generate_ai_chat_response(messages):
            await message.edit_text(response)
            await client.send_chat_action(chat_id, ChatAction.TYPING)


@app.on_message(filters.chat(chat_id) & filters.user('lor3m') & filters.regex('!gpt'))
async def switch_gpt_mode(client: Client, message: Message):
    global gpt_mode
    global messages
    gpt_mode = not gpt_mode

    await message.reply_text(f'GPT mode: {gpt_mode}')

    if gpt_mode:
        chat_history = {}

        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(1)

        if message.text != '!gpt':
            initial_text = message.text[4:]
        else:
            initial_text = 'You are a helpful assistant.'

        await client.send_message(
            chat_id,
            initial_text,
        )
        messages.append({
            'role': 'system',
            'content': initial_text
        })


# @app.on_message(her_message_filter)
# async def send_poop_reaction(client, message):
#     reaction = '💩'
#     await app.send_reaction(chat_id, message.id, reaction, big=True)

# Start the client and run it until manually stopped


app.run()
