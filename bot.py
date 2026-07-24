import os
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands

# שרת ווב קטן כדי ש-Render יישאר ער (Keep Alive)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# הגדרת הבוט
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong! 🏓 הבוט עובד!')

# הפעלה משולבת
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('MTUyOTU2ODY0OTc0MjkwOTYxMQ.Gx7b-a.u7XNYyB9hucL0LIO2yV0QEPCaSpUoR0bvbeEDk'))
