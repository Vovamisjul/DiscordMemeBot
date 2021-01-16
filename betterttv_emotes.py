import asyncio
import logging
import pickle

import aiohttp
from bs4 import BeautifulSoup, Tag

from phrases import download_content

logger = logging.getLogger(__name__)
EMOTE_COUNT = 300


class Emote:
    name: str
    image_url: str

    def __init__(self, name: str, id: str, type: str) -> None:
        self.name = name
        self.image_url = f"https://cdn.betterttv.net/emote/{id}/3x.{type}"


async def get_emotes():
    try:
        with open('temp/betterttv.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return await load_emotes()


async def load_emotes():
    logger.info("Loading betterttv emotes")
    curr_emote_count = 0
    popular_emotes = {}
    while curr_emote_count < EMOTE_COUNT:
        load_emote_count = EMOTE_COUNT - curr_emote_count if EMOTE_COUNT - curr_emote_count < 100 else 100
        async with aiohttp.ClientSession() as session:
            logger.info("Loading betterttv emotes from %s to %s", curr_emote_count, curr_emote_count+load_emote_count)
            async with session.get("https://api.betterttv.net/3/emotes/shared/trending",
                                   params={"offset": curr_emote_count, "limit": load_emote_count}) as response:
                emotes_json = await response.json()
                for entry in emotes_json:
                    emote_json = entry["emote"]
                    emote = Emote(emote_json["code"], emote_json["id"], emote_json["imageType"])
                    popular_emotes[emote.name] = emote
        curr_emote_count += 100
    with open('temp/betterttv.pickle', 'wb') as f:
        pickle.dump(popular_emotes, f)
    return popular_emotes


async def load_emotes_from_pages(pages_count):
    tasks = []
    default_url = "http://www.frankerfacez.com/emoticons/"

    async with aiohttp.ClientSession() as session:
        for i in range(1, pages_count + 1):
            url = default_url
            if i > 1:
                url += f"?page={i}"
            tasks.append(load_emotes_from(session, url))
        return await asyncio.gather(*tasks, return_exceptions=True)


async def load_emotes_from(session, url):
    emotes = {}
    logger.info("Loading emotes from %s", url)
    content = await download_content(session, url)
    soup = BeautifulSoup(content, "lxml")
    emotes_table = soup.select("#emote-form > table > tbody")[0].contents
    for emote_tag in emotes_table:
        if isinstance(emote_tag, Tag):
            emote = Emote()
            for element in emote_tag.children:
                if isinstance(element, Tag):
                    if "class" in element.attrs and "emote-name" in element.attrs["class"]:
                        for e in element.contents:
                            if isinstance(e, Tag) and e.name == "a":
                                emote.name = e.text
                    if len(element.contents) == 1 and isinstance(element.contents[0], str):
                        emote.usage_count = element.text
                    if "class" in element.attrs and "light" in element.attrs["class"]:
                        for e in element.contents:
                            if isinstance(e, Tag) and e.name == "img":
                                emote.image_url = e.attrs["src"][:-1] + "2"
            emotes[emote.name] = emote
    return emotes
