import os
import discord
from discord.ext import commands

token="MTQzOTY3NjgxMDExOTA5MDE3OA.GcaKqI.tFM7MMqUOzz3ShA2mXiIRcYAxE4x6kArTQO1kM"
PREFIX = "!"
# ayricaliklar (intents) değişkeni botun ayrıcalıklarını depolayacak
intents = discord.Intents.default()
# Mesajları okuma ayrıcalığını etkinleştirelim
intents.message_content = True
# client (istemci) değişkeniyle bir bot oluşturalım ve ayrıcalıkları ona aktaralım
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yaptık.')

@bot.command()
async def mem(ctx):
    with open('image/hmm.png', 'rb') as f:
        # Dönüştürülen Discord kütüphane dosyasını bu değişkende saklayalım!
        picture = discord.File(f)
   # Daha sonra bu dosyayı bir parametre olarak gönderebiliriz!
    await ctx.send(file=picture)

bot.run(token)