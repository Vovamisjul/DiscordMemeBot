from typing import Optional
import xml.etree.ElementTree as ET
import aiohttp

titles = {
    "анекдот": 1,
    "рассказ": 2,
    "стишок": 3,
    "тост": 6,
    "анекдот 18+": 11,
    "стишок 18+": 13,
    "тост 18+": 16,
}


async def get(title: str) -> Optional[str]:
    if title in titles:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://rzhunemogu.ru/Rand.aspx",
                                   params={"CType": titles[title]}) as response:
                content = await response.text(encoding="windows-1251")
                root = ET.fromstring(content)
                for child in root:
                    if child.tag == "content":
                        return child.text
    return None
