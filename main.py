import disnake
from disnake.ext import commands
import openai
from PIL import Image
import io
import pytesseract
import wikipedia
from datetime import datetime, timedelta
import random

memes = [
    "C:\\Users\\ytiva\\PycharmProjects\\pythonProject15\\mem.jpg",
    "C:\\Users\\ytiva\\PycharmProjects\\pythonProject15\\mem.jpeg",
    "C:\\Users\\ytiva\\PycharmProjects\\pythonProject15\\mem (2).jpg",
]

from bs4 import BeautifulSoup

def get_random_fact_from_internet():
    facts = [
        "Кошки спят в среднем 12-16 часов в день.",
        "Медузы не имеют ни мозга, ни сердца.",
        "Акулы существуют уже более 420 миллионов лет.",
        "Дельфины могут узнавать себя в зеркале.",
        "Пчелы совершают около 200-300 полетов в день.",
        # Добавьте еще факты...
    ]
    return random.choice(facts)

import requests

user_last_message = {}

# Устанавливаем токен и ключ от OpenAI
TOKEN = 'MTEyMTg3NTg5ODkxNjkzNzc4MA.GPt_oT.F5ni-PO4dtV4K-ciNEW-Whlr5dNOOmYasoSdc4'
API_KEY = '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'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

banned_words = ["сука", "умри", "сдохни", "блять", "порно", "член", "еблан", "уебан", "пидор", "гей", "пидорас", "соси", "уебище", "хуй"]

# Создаем экземпляр клиента Disnake
intents = disnake.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Инициализируем переводчик
@bot.event
async def on_ready():
    print(f'Бот подключился как {bot.user}')
    await bot.change_presence(activity=disnake.Streaming(name="POKER", url="https://www.twitch.tv/jesusavgn"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Проверяем наличие запрещенных слов
    for word in banned_words:
        if word in message.content:
            await message.delete()
            return

    mentioned = bot.user.mentioned_in(message)
    should_respond = random.random() < 0.2 and not mentioned

    if mentioned or should_respond:
        await message.channel.send("Печатает...")

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=message.content,
            max_tokens=2000,
            n=2,
            temperature=0.3,  # Можете использовать другое значение temperature
            api_key=API_KEY
        )

        reply = f'{message.author.mention}, {response.choices[0].text.strip()}'

        # Create a random color embed and set the reply as the description
        random_color = disnake.Color.random()
        embed = disnake.Embed(description=reply, color=random_color)

        await message.channel.send(embed=embed)
    else:
        if not mentioned and random.random() < 0.1:
            fact = get_random_fact_from_internet()
            await message.channel.send(f"Интересный факт: {fact}")

    await bot.process_commands(message)
@bot.command()
async def image(ctx):
    if len(ctx.message.attachments) == 0:
        await ctx.send("Необходимо прикрепить изображение.")
        return

    attachment = ctx.message.attachments[0]

    if not attachment.content_type.startswith("image/"):
        await ctx.send("Прикрепленный файл должен быть изображением.")
        return

    image_data = await attachment.read()
    image = Image.open(io.BytesIO(image_data))

    text = pytesseract.image_to_string(image)

    await ctx.send(f"Текст на изображении: {text}")

    await ctx.send(file=disnake.File(io.BytesIO(image_data), filename="image.png"))

@bot.slash_command()
async def wikisearch(ctx, *, query):
    try:
        page = wikipedia.page(query)
        title = page.title
        summary = wikipedia.summary(query, sentences=3)
        url = page.url

        embed = disnake.Embed(title=title, description=summary, url=url, color=0x00ff00)
        await ctx.send(embed=embed)

    except wikipedia.exceptions.DisambiguationError as e:
        options = "\n".join(e.options)
        await ctx.send(f"Уточните запрос. Найдены несколько возможных вариантов:\n\n{options}")

    except wikipedia.exceptions.PageError:
        await ctx.send(f"Не удалось найти статью с запросом: {query}")

@bot.slash_command()
async def randomwiki(ctx):
    result = random_page()
    await ctx.send(result)

def random_page():
    random_page_title = wikipedia.random(pages=1)
    try:
        page = wikipedia.page(random_page_title)
        result = page.summary
    except wikipedia.exceptions.DisambiguationError as e:
        result = random_page()
    return result

@bot.slash_command()
async def ivent(ctx):
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(['+', '-', '*', '/'])

    question = f"Решите математическую задачу:\n{num1} {operator} {num2} = ?"

    await ctx.send(question)

    def check_answer(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        user_answer_message = await bot.wait_for('message', check=check_answer, timeout=10)
        user_answer = user_answer_message.content

        correct_answer = calculate_answer(num1, num2, operator)

        if user_answer == str(correct_answer):
            await ctx.send("Правильно! Вы решили задачу.")
        else:
            await ctx.send(f"Неправильно. Правильный ответ: {correct_answer}")

    except TimeoutError:
        await ctx.send("Время истекло. Викторина завершена.")

def calculate_answer(num1, num2, operator):
    if operator == '+':
        return num1 + num2
    elif operator == '-':
        return num1 - num2
    elif operator == '*':
        return num1 * num2
    elif operator == '/':
        return num1 / num2


bot.run(TOKEN)