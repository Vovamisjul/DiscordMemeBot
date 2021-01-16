trigger_words = [(("niger", "nigger", "niga", "nigga", "bruh", "black", "coloured", "нигер", "ниггер", "нига", "ниге", "нигу", "ниги", "нигга", "ниггу", "нигге", "нигги",
                   "брах", "брух", "черн", "негр", "цветн"), "niger"),
                 (("pidor", "pidr", "gay", "пидр", "пидор", "пидар", "гей", "голубой"), "pidor"),
                 (("dota", "дота", "доту", "доте", "доты"), chr(0x7FB)), ]


def char_to_emoji(char):
    return chr(ord(char) - ord("a") + 0x1F1E6)


async def send_word_as_reaction(word, message):
    for letter in word:
        await message.add_reaction(char_to_emoji(letter))


async def add_reaction_if_possible(message):
    for trigger in trigger_words:
        for trigger_word in trigger[0]:
            if trigger_word in message.content.lower():
                await send_word_as_reaction(trigger[1], message)
                return
