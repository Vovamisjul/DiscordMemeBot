import json
from typing import Optional

import aiohttp

urls = {
    "анекдот": "generator-anekdotov-online",
    "цитату": "generator-citat-online",
    "факт": "generator-interesnykh-faktov",
}

base_url = "https://castlots.org/"


async def get(title: str) -> Optional[str]:
    if title in urls:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://castlots.org/{urls[title]}/generate.php",
                                    headers={"X-Requested-With": "XMLHttpRequest"},
                                    data={"hid": "yes"}) as response:
                content = await response.text()
                content = json.loads(content)
                return content["va"]
    return None
