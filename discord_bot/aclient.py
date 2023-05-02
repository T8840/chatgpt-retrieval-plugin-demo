import os
import discord
from typing import Union
from dotenv import load_dotenv
from discord import app_commands
import log
logger = log.setup_logger(__name__)
load_dotenv()


class aclient(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.listening, name="/chat | /help")
        self.is_replying_all = "True"


    async def send_message(self, message, user_message):
        try:
            author = message.user.id
            response = (f'> **{user_message}** - <@{str(author)}>  \n\n')
            char_limit = 1900
            # if len(response) > char_limit:
            #     # Split the response into smaller chunks of no more than 1900 characters each(Discord limit is 2000 per chunk)
            #     if "```" in response:
            #         # Split the response if the code block exists
            #         parts = response.split("```")
            #
            #         for i in range(len(parts)):
            #             if i % 2 == 0:  # indices that are even are not code blocks
            #                 if self.is_replying_all == "True":
            #                     await message.channel.send(parts[i])
            #                 else:
            #                     await message.followup.send(parts[i])
            #             else:  # Odd-numbered parts are code blocks
            #                 code_block = parts[i].split("\n")
            #                 formatted_code_block = ""
            #                 for line in code_block:
            #                     while len(line) > char_limit:
            #                         # Split the line at the 50th character
            #                         formatted_code_block += line[:char_limit] + "\n"
            #                         line = line[char_limit:]
            #                     formatted_code_block += line + "\n"  # Add the line and seperate with new line
            #
            #                 # Send the code block in a separate message
            #                 if (len(formatted_code_block) > char_limit + 100):
            #                     code_block_chunks = [formatted_code_block[i:i + char_limit]
            #                                          for i in range(0, len(formatted_code_block), char_limit)]
            #                     for chunk in code_block_chunks:
            #                         if self.is_replying_all == "True":
            #                             await message.channel.send(f"```{chunk}```")
            #                         else:
            #                             await message.followup.send(f"```{chunk}```")
            #                 elif self.is_replying_all == "True":
            #                     await message.channel.send(f"```{formatted_code_block}```")
            #                 else:
            #                     await message.followup.send(f"```{formatted_code_block}```")
            #     else:
            #         response_chunks = [response[i:i + char_limit]
            #                            for i in range(0, len(response), char_limit)]
            #         for chunk in response_chunks:
            #             if self.is_replying_all == "True":
            #                 await message.channel.send(chunk)
            #             else:
            #                 await message.followup.send(chunk)
            # elif self.is_replying_all == "True":
            if self.is_replying_all == "True":
                await message.channel.send(response)
            else:
                await message.followup.send(response)
        except Exception as e:
            if self.is_replying_all == "True":
                await message.channel.send(
                    f"> **ERROR: Something went wrong, please try again later!** \n ```ERROR MESSAGE: {e}```")
            else:
                await message.followup.send(
                    f"> **ERROR: Something went wrong, please try again later!** \n ```ERROR MESSAGE: {e}```")
            logger.exception(f"Error while sending message: {e}")

client = aclient()
