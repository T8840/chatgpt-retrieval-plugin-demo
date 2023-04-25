import discord # Import discord.py
from discord.ext import commands # Import commands from discord.py
from secrets import DISCORD_BOT_TOKEN as token
from secrets import OPENAI_API_KEY
from chat_utils import ask
from database_utils import upsert,generate_uuid
import openai
openai.api_key = OPENAI_API_KEY

# Create a new bot
intents = discord.Intents.default()
intents.message_content = True
import logging

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        # print("message",message)
        response = ask(message.content)
        await message.channel.send(response)
    else:
        if message.author != bot.user:
            discord_uuid = generate_uuid('discord', message.content)
            upsert(discord_uuid,message.content)
        await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'Logged into Discord as {bot.user}')
    activity = discord.Game(name="milady", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

bot.run(token)