import asyncio
import logging
import os
import random
import re

import aiohttp
import discord
import pyttsx3

import bad_words
import betterttv_emotes
import phrases
import race_buller
import story_teller
import weird_generator

logger = logging.getLogger(__name__)


class NiggerBot(discord.Client):
    ARTEM_ID = "8452"
    PAVLOV_URL = "http://localhost:5000/model"

    def __init__(self, **options):
        super().__init__(**options)
        self.talkativeness_phrases, self.send_phrases, self.thanks_phrases, self.betterttv_emotes = \
            tuple(asyncio.get_event_loop().run_until_complete(self.load_content()))
        self.id = int(os.getenv("CLIENT_ID"))
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 145)

    @staticmethod
    async def load_content():
        return await asyncio.gather(phrases.get_talkativeness(), phrases.get_send(), phrases.get_thanks(),
                                    betterttv_emotes.get_emotes())

    async def on_message(self, message):
        if message.author.discriminator == self.ARTEM_ID:
            await message.add_reaction("\U0001F1F5\U0001F1F1")

        await asyncio.gather(bad_words.add_reaction_if_possible(message),
                             self.check_for_betterttv(message),
                             self.try_to_voice_message(message),
                             self.try_to_get_fact(message),
                             )

        if message.tts:
            await message.channel.send(f"<@{message.author.id}> {random.choice(self.talkativeness_phrases)}")

        if any(mention for mention in message.mentions if mention.id == self.id):
            reg = re.match(r"^<.*> ", message.content)  # remove mention
            text = message.content[reg.end():]
            async with aiohttp.ClientSession() as session:
                async with session.post(self.PAVLOV_URL, json={"x": [text]}) as response:
                    sentiment = await response.json()
                    if "negative" in sentiment[0]:
                        await message.channel.send(f"<@{message.author.id}> {random.choice(self.send_phrases)}")
                    elif "positive" in sentiment[0]:
                        await message.channel.send(f"<@{message.author.id}> {random.choice(self.thanks_phrases)}")

        people_on_photo = race_buller.who_is_it(attachment.url for attachment in message.attachments)
        if people_on_photo:
            await message.channel.send(people_on_photo)

    async def check_for_betterttv(self, message):
        contains_not_betterttv = False
        for word in message.content.split(" "):
            if word in self.betterttv_emotes:
                await message.channel.send(self.betterttv_emotes[word].image_url)
            elif word != "":
                contains_not_betterttv = True

        if not contains_not_betterttv and len(message.content) > 0:
            await message.delete()

    async def try_to_voice_message(self, message):
        if message.content.startswith("/say") and message.author.voice:
            text_to_say = message.content[5:]
            try:
                story = await story_teller.get(text_to_say)
                if story:
                    self.engine.save_to_file(story, "temp/voice.mp3")
                else:
                    self.engine.save_to_file(text_to_say, "temp/voice.mp3")
                self.engine.runAndWait()
                channel = message.author.voice.channel

                vc = await channel.connect()

                vc.play(discord.FFmpegPCMAudio("temp/voice.mp3",
                                               executable="D:/Programs/ffmpeg/ffmpeg-4.3.1-2020-11-19-full_build/bin/ffmpeg.exe"))
                while vc.is_playing():
                    await asyncio.sleep(.1)
                await vc.disconnect()
            except ValueError as e:
                logger.error(e)

    async def try_to_get_fact(self, message):
        if message.content.startswith("сгенерируй"):
            words = message.content.split(" ")
            if len(words) < 2:
                return
            if len(words) == 2:
                words.append("")
            result = await weird_generator.generate(words[1], words[2])
            if result:
                await message.channel.send(result)