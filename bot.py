import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# 1. שרת Keep Alive מובנה (שומר על הבוט ער ב-Render)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. הגדרת הבוט של דיסקורד
intents = discord.Intents.default()
intents.message_content = True  # חובה כדי שהבוט יוכל לקרוא הודעות

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong! 🏓 הבוט עובד ומחובר בהצלחה!')

# 3. הפעלה משולבת של השרת והבוט יחד
if __name__ == "__main__":
    keep_alive()
    # הבוט מתחבר בעזרת הטוקן ששמרת בהגדרות של Render
    bot.run(os.getenv('MTUyOTU2ODY0OTc0MjkwOTYxMQ.Gx7b-a.u7XNYyB9hucL0LIO2yV0QEPCaSpUoR0bvbeEDk'))
