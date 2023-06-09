import discord # Import discord.py
from discord.ext import commands # Import commands from discord.py
from secrets import DISCORD_BOT_TOKEN as token
from secrets import OPENAI_API_KEY
from api.chat_utils import ask
from api.database_utils import upsert,generate_uuid,upsert_file
import openai
import os
import json
import aiohttp
openai.api_key = OPENAI_API_KEY


def run_discord_bot():
    # Create a new bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)


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
                pass
                # discord_uuid = generate_uuid('discord', message.content)
                # upsert(discord_uuid,message.content)
            await bot.process_commands(message)

    @bot.event
    async def on_ready():
        print(f'Logged into Discord as {bot.user}')
        activity = discord.Game(name="chatgpt", type=3)
        await bot.change_presence(status=discord.Status.online, activity=activity)


    @bot.command(name="helps")
    async def helps(ctx):
        await ctx.send(f"This is the help command!")


    @bot.command(name='send', help='Send Message to the AI assistant.')
    async def send(ctx, *, message: str):
        server_id = ctx.guild.id
        server_name = ctx.guild.name
        discord_uuid = generate_uuid('discord_' + server_name, message)
        upsert(discord_uuid, content = message,source_id = int(server_id),author=ctx.author.name )
        await ctx.send("Message received!")

        # responses = load_responses()
        # if str(server_id) not in responses:
        #     responses[str(server_id)] = {
        #         'server_name': server_name,
        #         'responses': []
        #     }
        #
        # response = {
        #     'author': ctx.author.name,
        #     'message': message,
        #     'response': '这是一个示例回复'  # 在这里添加您的自定义逻辑以生成不同的回复
        # }
        #
        # responses[str(server_id)]['responses'].append(response)
        # save_responses(responses)
        # await ctx.send(f"{ctx.author.mention} 发送了: {message}，回复： {response['response']}")


    @bot.command(name='chat', help='Talk to the AI assistant.')
    async def chat(ctx, *, message: str):
        server_id = str(ctx.guild.id)
        server_name = ctx.guild.name
        response = ask(message,source_id=server_id)
        await ctx.send(f"{ctx.author.mention} {response}")

    @bot.command(name='upload', help='Upload file to AI assistant.')
    async def upload(ctx: commands.Context):
        server_id = str(ctx.guild.id)
        server_name = ctx.guild.name
        if len(ctx.message.attachments) > 0:
            attachment = ctx.message.attachments[0]
            file_url = attachment.url
            file_name = attachment.filename
            local_file_path = os.path.join("../uploads", file_name)

            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as resp:
                    with open(local_file_path, "wb") as f:
                        while True:
                            chunk = await resp.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)

            await ctx.send("File received and saved!")
            upsert_file(filename=file_name,source_id=server_id)
        else:
            await ctx.send("No file attached.")

    @upload.error
    async def upload_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("An error occurred: Missing required argument.")
        else:
            await ctx.send("An unexpected error occurred.")


    def load_responses():
        if not os.path.exists('responses.json'):
            with open('responses.json', 'w') as f:
                json.dump({}, f)

        with open('responses.json', 'r') as f:
            return json.load(f)

    def save_responses(responses):
        with open('responses.json', 'w') as f:
            json.dump(responses, f, indent=2)

    @bot.event
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
        #     await general_channel.send("Hello! I'm your new Discord bot!")
        # else:
        #     print("General channel not found.")

    bot.run(token)