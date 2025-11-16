# img_name=random.choice(os.listdir('image'))
import os
import discord
from discord.ext import commands
from logic import gen_pass
from game import MinesweeperGame

token="token"
PREFIX = "!"
# ayricaliklar (intents) değişkeni botun ayrıcalıklarını depolayacak
intents = discord.Intents.default()
# Mesajları okuma ayrıcalığını etkinleştirelim
intents.message_content = True
# client (istemci) değişkeniyle bir bot oluşturalım ve ayrıcalıkları ona aktaralım
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
aktif_oyunlar = {}

class MyClient(discord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: discord.ClientUser

    async def on_message(self, message):
        if message.content.startswith('!deleteall'):
            msg = await message.channel.send('I will delete myself now...')
            await msg.delete()

            # this also works
            await message.channel.send('Goodbye in 3 seconds...', delete_after=3.0)

    async def on_message_delete(self, message):
        msg = f'{message.author} has deleted the message: {message.content}'
        await message.channel.send(msg)

client =MyClient(intents=intents)


async def goster(message, g, mail):
    await message.channel.send(f"```\n{g.get_board_display(show_all=not g.is_playing)}\n```")
    if mail:
        await message.channel.send(mail)

@bot.command()
async def mem(ctx):
    with open('image/hmm.png', 'rb') as f:
        # Dönüştürülen Discord kütüphane dosyasını bu değişkende saklayalım!
        picture = discord.File(f)
   # Daha sonra bu dosyayı bir parametre olarak gönderebiliriz!
    await ctx.send(file=picture)


@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yaptık.')

@bot.event
async def on_message(message):
    # Botun kendi mesajlarını yok say
    if message.author == bot.user:
        return

    content = message.content.strip()
    cid = message.channel.id

    if content.startswith('merhaba'):
        await message.channel.send("Selam!")
        return

    if content.startswith('bye'):
        await message.channel.send("\U0001f642")
        return

    if content.startswith('$sifre'):
        await message.channel.send("Şifre oluşturuldu: " + gen_pass(10))
        return

    if content.startswith(f'{PREFIX}başlat') or content.startswith(f'{PREFIX}start'):
        parts = content.split()
        try:
            m = int(parts[1]) if len(parts) > 1 else 10  # Mayın sayısını al, yoksa 10
            if m not in [10, 20, 30]:
                raise ValueError
        except (IndexError, ValueError):
            return await message.channel.send("Hata: Mayın sayısı 10, 20 veya 30 olmalıdır. Örn: `!başlat 20`")

        g = MinesweeperGame(m)
        aktif_oyunlar[cid] = g
        await message.channel.send(f"💣 **{m} Mayınlı** oyun başladı! Hamle: `!oyna K2b`")
        await goster(message, g, "Tahta Durumu:")
        return

    if content.startswith(f'{PREFIX}oyna') or content.startswith(f'{PREFIX}p'):
        g = aktif_oyunlar.get(cid)
        if not g or not g.is_playing:
            return await message.channel.send(f"Hata: Önce `{PREFIX}başlat` ile oyun başlatın.")

        parts = content.split()
        if len(parts) != 2 or len(parts[1]) != 3:
            return await message.channel.send("Hata: Komut: `!oyna K2b` (3 karakterli kod) olmalıdır.")

        move = parts[1]
        action, x_str, y_str = move[0].upper(), move[1], move[2].lower()

        if action not in ['K', 'B']:
            return await message.channel.send("Hata: Hamle 'K' (Kazma) veya 'B' (Bayrak) olmalıdır.")

        # Hareketi işle
        sonuc_mesaj = g.handle_action(action, x_str, y_str)
        await goster(message, g, sonuc_mesaj)

        # Oyun bitimi
        if not g.is_playing:
            if g.game_won:
                final_mesaj = "\U0001F3C6 OYUN BİTTİ: KAZANDINIZ!"
            else:
                final_mesaj = "\U00002620 OYUN BİTTİ: KAYBETTİNİZ!"
            await message.channel.send(f"**{final_mesaj}** Tekrar oynamak ister misiniz? (`{PREFIX}başlat 10`)")
            del aktif_oyunlar[cid]
        return

    # Varsayılan: gelen mesajı aynen gönder
    await message.channel.send(message.content)


bot.run(token)
client.run(token)
