import discord # Import discord.py
from secrets import DISCORD_BOT_TOKEN as token
from secrets import OPENAI_API_KEY
from discord_bot.aclient import client
from api.database_utils import upsert,generate_uuid,upsert_file
from api.chat_utils import ask

import openai
import os
import json
import log
import aiohttp

logger = log.setup_logger(__name__)

openai.api_key = OPENAI_API_KEY

def run_discord_bot():
    @client.event
    async def on_message(message):

        if message.author == client.user:
            return

        if client.user.mentioned_in(message):
            # print("message",message)
            response = ask(message.content)
            await message.channel.send(response)
        else:
            if message.author != client.user:
                pass
                # discord_uuid = generate_uuid('discord', message.content)
                # upsert(discord_uuid,message.content)
            # await client.process_commands(message)

    @client.event
    async def on_ready():
        await client.tree.sync()
        print(f'Logged into Discord as {client.user}')
        activity = discord.Game(name="chatgpt", type=3)
        await client.change_presence(status=discord.Status.online, activity=activity)


    @client.tree.command(name="help", description="Show help for the bot")
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(""":star: **BASIC COMMANDS** \n
        - `/chat [message]` Chat with ChatGPT!
        - `/send [message]` Send information to the ChatGPT!
        - `/upload [file.txt]` Upload file.txt to the ChatGPT!
                """)

        logger.info(
            "\x1b[31mSomeone needs help!\x1b[0m")

    @client.tree.command(name='send', description='Send Message to the AI assistant.')
    async def send(interaction: discord.Interaction, *, message: str):
        await interaction.response.defer()

        server_id = str(interaction.guild.id)
        server_name = interaction.guild.name
        discord_uuid = generate_uuid('discord_' + server_name, message)
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.send_message(interaction,"Message received!")
        upsert(discord_uuid, content = message,source_id = int(server_id),author=username )
        await interaction.edit_original_response(content="response:")


    @client.tree.command(name='chat', description='Talk to the AI assistant.')
    async def chat(interaction: discord.Interaction, *,message: str):
        await interaction.response.defer()
        server_id = str(interaction.guild.id)
        server_name = interaction.guild.name
        response = ask(message,source_id=server_id)
        await client.send_message(interaction, f"{response}")
        await interaction.edit_original_response(content="response:")


    @client.tree.command(name='upload', description='Upload file to AI assistant.')
    async def upload(interaction, file: discord.Attachment):
        await interaction.response.defer()

        server_id = str(interaction.guild.id)
        server_name = interaction.guild.name
        file_url = file.url
        file_name = file.filename
        local_file_path = os.path.join("uploads", file_name)

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                with open(local_file_path, "wb") as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
        await client.send_message(interaction, "File received and saved!")
        upsert_file(filename=file_name,source_id=server_id)
        await interaction.edit_original_response(content="response:")


    @upload.error
    async def upload_error(interaction, error):
        if isinstance(error, interaction.MissingRequiredArgument):
            await interaction.channel.ssend("An error occurred: Missing required argument.")
        else:
            await interaction.channel.ssend("An unexpected error occurred.")


    def load_responses():
        if not os.path.exists('responses.json'):
            with open('responses.json', 'w') as f:
                json.dump({}, f)

        with open('responses.json', 'r') as f:
            return json.load(f)

    def save_responses(responses):
        with open('responses.json', 'w') as f:
            json.dump(responses, f, indent=2)

    @client.event
    async def on_guild_join(guild):
        print(f"Joined new server: {guild.name} with ID: {guild.id}")

        # general_channel = None
        # for channel in guild.text_channels:
        #     if channel.name == "general":
        #         general_channel = channel
        #         break
        #
        # if general_channel:
        #     print(f"Found general channel with ID: {general_channel.id}")
        #     await general_channel.send("Hello! I'm your new Discord client!")
        # else:
        #     print("General channel not found.")



    client.run(token)