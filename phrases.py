import asyncio
import pickle
import time

import aiohttp
from bs4 import BeautifulSoup, Tag
import requests
import logging
import re

logger = logging.getLogger(__name__)


async def get_talkativeness():
    try:
        with open('temp/talkativeness.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return await load_talkativeness()


async def load_talkativeness():
    logger.info("Loading talkativeness phrases")
    phrases = await load_talkativeness_from_all_pages()
    logger.info("Ended loading talkativeness phrases")
    phrases_list = [item for sublist in phrases for item in sublist]
    with open('temp/talkativeness.pickle', 'wb') as f:
        pickle.dump(phrases_list, f)
    return phrases_list


async def load_talkativeness_from_all_pages():
    tasks = []
    default_url = "http://www.aforism.su"
    async with aiohttp.ClientSession() as session:
        for i in range(1, 7):
            index = f"5_{i}" if i > 1 else "5"
            url = f"{default_url}/{index}.html"
            tasks.append(parse_talkativeness(session, url))
        return await asyncio.gather(*tasks, return_exceptions=True)


async def parse_talkativeness(session, url):
    phrases = []
    logger.info("Loading talkativeness from %s", url)
    content = await download_content(session, url)
    soup = BeautifulSoup(content, "lxml")
    phrases_tag = soup.select("body > center > table:nth-child(2) > tr > td.center > "
                              "table > tr:nth-child(2) > td")[0].contents
    phrase = "\""
    for element in phrases_tag:
        if isinstance(element, str):
            phrase += element.strip()
            continue
        if element.name == 'a':
            phrase += element.text.strip()
            continue
        if element.name == 'p' and type(element.next) is Tag:
            phrase += f"\" ({element.text.strip()})"
            phrases.append(phrase)
            phrase = "\""

    return phrases


async def get_send():
    try:
        with open('temp/send.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return await load_send()


async def load_send():
    phrases = []
    url = "https://mensby.com/career/psychology/kak-kulturno-poslat-cheloveka-120-primerov"
    logger.info("Loading send phrases from %s", url)
    async with aiohttp.ClientSession() as session:
        soup = BeautifulSoup(await download_content(session, url), "lxml")
        phrases_tag = soup.select("body > div.jeg_viewport > div.post-wrapper > div:nth-child(1) > div.jeg_main > "
                                  "div > div > div > div.row > div.jeg_main_content.col-md-8 > div > "
                                  "div.entry-content.no-share > div.content-inner")[0].contents
        for element in phrases_tag:
            if element.name == 'p' and isinstance(element.next, str):
                result = re.match(r"^\d+\. ", element.next)
                if result:
                    phrases.append(element.next[result.end():])

    logger.info("Ended loading send phrases")
    with open('temp/send.pickle', 'wb') as f:
        pickle.dump(phrases, f)
    return phrases


async def get_thanks():
    try:
        with open('temp/thanks.pickle', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return await load_thanks()


async def load_thanks():
    phrases = []
    url = "https://sinonim.org/s/%D1%81%D0%BF%D0%B0%D1%81%D0%B8%D0%B1%D0%BE"
    logger.info("Loading thanks phrases from %s", url)
    async with aiohttp.ClientSession() as session:
        soup = BeautifulSoup(await download_content(session, url), "lxml")
        for i in range(1, 28):
            phrases.append(soup.select(f"#tr{i} > :nth-child(2) > a")[0].text)
        logger.info("Ended loading thanks phrases")
        with open('temp/thanks.pickle', 'wb') as f:
            pickle.dump(phrases, f)
        return phrases


async def download_content(session, url):
    async with session.get(url) as response:
        return await response.text()


if __name__ == "__main__":
    load_talkativeness()
    load_send()
