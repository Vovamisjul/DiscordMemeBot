import asyncio
import logging
import os

from nigger_bot import NiggerBot
from dotenv import load_dotenv

async def kek(client, token):
    return await asyncio.gather(client.start(token))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TOKEN")
client = NiggerBot()
asyncio.get_event_loop().run_until_complete(kek(client, TOKEN))
