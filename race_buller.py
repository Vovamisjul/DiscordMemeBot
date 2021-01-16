import random

import requests
from deepface import DeepFace
import base64

names = {"asian": ("чинг чонг", "узкоглазый", "китаец", "азиат", "желторотик"),
         "indian": ("индус", "индеец... или это не то", "хинду"),
         "black": ("нигер", "черномазый", "черножопый", "раб", "оишбка природы",),
         "white": ("представитель высшей расы", "светлокожий господин",),
         "middle eastern": ("европеец", "представитель высшей расы", "светлокожий господин", "чистокровный ариец",),
         "latino hispanic": ("латинос", "мексиканец", "мучачо"), }


def who_is_it(urls):
    people = []
    for url in urls:
        try:
            people.append(random.choice(names[get_race_from_image(url)]))
        except ValueError as e:  # just ignore if there are no people on photo
            pass
    if any(people):
        result = f"О, это же {people[0]}"
        for i in range(1, len(people)):
            if i < len(people) - 1:
                result += f", {people[i]}"
            else:
                result += f" и {people[i]}"
        result += "!"
        return result
    return None


def get_race_from_image(url):
    image = "data:image/," + base64.b64encode(requests.get(url).content).decode()
    obj = DeepFace.analyze(image, actions=["race"])
    return obj["dominant_race"]
