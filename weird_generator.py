import json
from typing import List, Optional

from aiohttp import ClientSession

urls = {
    "ник": "generator-nikov-online",
    "слово": "generator-slov",
    "слоган": "generator-sloganov",
    "рифму": "podbor-rifmi-k-slovu",
}


async def generate(subject: str, param: str) -> Optional[str]:
    if subject in urls:
        async with ClientSession() as session:
            async with session.post(f"https://castlots.org/{urls[subject]}/generate.php",
                                    headers={"X-Requested-With": "XMLHttpRequest"},
                                    data={"word": param}) as response:
                content = await response.text()
                content = json.loads(content)
                if content["success"]:
                    return content["va"]
                elif content["errors"]:
                    return content["errors"]
                else:
                    return None
    return None
