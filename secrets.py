from dotenv import load_dotenv
import os
load_dotenv()

token = os.getenv('OPENAI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DATABASE_INTERFACE_BEARER_TOKEN = os.getenv('DATABASE_INTERFACE_BEARER_TOKEN')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

SOURCE = "email"
SOURCE_ID = 1
HOST = "https://nealdiscord.fly.dev"
