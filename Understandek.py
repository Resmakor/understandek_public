from audioop import add
from dis import dis
from email import message
from email.errors import MessageError
from itertools import count
from re import X
from sqlite3 import Timestamp
from sys import prefix
from tabnanny import check
from tracemalloc import start
from xml import dom
import colour

import discord
from discord.ext import commands

from discord.ext.commands import has_permissions #to gdybym chcial zrobic bany

from discord.ext.commands import Bot
import random

import youtube_dl
import search_link
from discord import Spotify
from discord.utils import get 
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from colorthief import ColorThief

import asyncio
import validators
import datetime


from pytube import YouTube
from pytube import Playlist
import re
import time

import os
from dotenv import load_dotenv
load_dotenv()

bot_prefix = ","

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.presences = True
client = commands.Bot(command_prefix = bot_prefix, intents = intents)

token = os.environ['token']
bot_id = int(os.environ['bot_id'])

client.remove_command("help")

@client.event
async def on_ready():
    print("Understandek is online")
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "Young Leosia - Szklanki"))

@client.event
async def on_message(message):
    if message.author.bot == False and message.content != str(bot_prefix):
        slowa = ['xd', 'xD', 'XD', 'Xd']
        for slowo in slowa:
            if slowo in message.content:
                if slowo == 'Xd':
                    await message.channel.send('Tak sie nie pisze "XD" mordo')
                else:
                    await message.channel.send('Co cie tak smieszy XD')
    await client.process_commands(message)

@client.command()
async def join(ctx):
    if not ctx.guild.voice_client in client.voice_clients:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.channel.send('I am in the voice channel!')

@client.command()
async def dc(ctx):
    if ctx.guild.voice_client in client.voice_clients:
        await ctx.send('See you soon!', tts = True, delete_after = 4)
        await ctx.voice_client.disconnect()
    else:
        await ctx.channel.send('I am not in the voice channel!')

@client.command()
async def listen(ctx, member : discord.Member):
    sname = member.activity.title
    sartists = member.activity.artists
    album = member.activity.album
    palbum = member.activity.album_cover_url
    duration = member.activity.duration
    quick_embed = discord.Embed(title = f"{member} slucha teraz {sname} z albumu {album}, sa tam artysci: {sartists}", description = f'Song duration **{duration}**', colour = 0xeb1e1e)
    quick_embed.set_thumbnail(url = palbum)
    await ctx.channel.send(embed = quick_embed)

@client.command()
async def cannon(ctx, member : discord.Member):
    działonowy = discord.utils.find(lambda r: r.name == 'Działonowy', ctx.message.guild.roles)
    if działonowy in ctx.author.roles:
        current_channel = member.voice.channel.id
        channel_ids = [748293007765274654, 690951616047742996, 753960037164122245, 690951721874096239, 782001116313288734]
        if current_channel not in channel_ids:
            channel_ids.append(current_channel)

        for channel_id in channel_ids:
            channel = client.get_channel(channel_id)
            await member.move_to(channel)
        gif_embed = discord.Embed(title = "KABOOM!")
        gif_embed.set_image(url = "https://media4.giphy.com/media/76zpU8jlNo5EHoEpjb/giphy.gif")
        await ctx.channel.send(f'{member.mention} has been blown up!', embed = gif_embed)
    else:
        await ctx.channel.send('You do not have sufficient permissions!')

# Function adds song to list of songs
list_of_songs = []
def add_to_queue(url):
    global list_of_songs
    list_of_songs.append(str(url))

# Function adds song to embed
embed_queue = discord.Embed(title = "Kolejka  🎵 🎵 🎵", url = "https://github.com/Resmakor", color = 0x8FE40C)
def add_to_embed(video_title, url, duration):
    global embed_queue
    min_dur = datetime.timedelta(seconds = duration)
    value_to_be_given = f"Estimated time: {min_dur} " + url
    embed_queue.add_field(name = f"{video_title}", value = value_to_be_given, inline = False)

# Showing status of queue
@client.command()
async def queue(ctx):
    global embed_queue
    await ctx.channel.send(embed = embed_queue, delete_after = 30)

# Function shows which song is being played and add reactions to some of them
async def show_status(ctx, video_title, duration, id, colour_id):
    min_dur = datetime.timedelta(seconds = duration)
    quick_embed = discord.Embed(title = f"**{video_title}** 🎵", description = f'Song duration **{min_dur}**', color = colour_id)
    quick_embed.set_thumbnail(url = f"https://img.youtube.com/vi/{id}/sddefault.jpg")

    await ctx.channel.send(embed = quick_embed)
    await client.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = video_title))
    
    title_to_upper = video_title.upper()
    giga_chad = ['LEOSIA', 'SENTINO', 'POWW']
    stinky_cheese = ['SZPAKU', 'CHIVAS']

    for slowo in giga_chad:
        if slowo in title_to_upper:
            await ctx.message.add_reaction("❤️")
            break

    for slowo in stinky_cheese:
        if slowo in title_to_upper:
            await ctx.message.add_reaction("🥶")
            await ctx.message.add_reaction("🤮")
            await ctx.message.author.send("Zastanow sie nad soba :)")
            break

# Function shows time of a song already set
async def show_time(ctx, timer : str):
    await ctx.channel.send(f'Current time set to: **{timer}**', delete_after = 10)

# Saved ctx's
ctx_queue = []
if_loop = False
FFMPEG_OPTIONS = {'before_options': '-ss 00:00:00.00 -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
previous_hours = previous_minutes = previous_seconds = 0

# Function plays music in 'queue' order
# Time.sleep is used to fixed bug with voice.is_playing(), it was sending true value when there was no music playing
def play_queue():
    global FFMPEG_OPTIONS, ctx_queue, list_of_songs, started_time, previous_hours, previous_minutes, previous_seconds
    print(list_of_songs)
    
    if len(list_of_songs) > 0:
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(list_of_songs[0], download = False)
                video_title = info.get('title', None)
                global duration
                duration = info['duration']

        ctx = ctx_queue[0]
        time.sleep(0.2)
        voice = get(client.voice_clients, guild = ctx.guild)

        if not voice.is_playing():
            global if_loop
            started_time = 0
            URL = info['formats'][0]['url']
            ids = re.findall(r"watch\?v=(\S{11})", list_of_songs[0])
            id = ids[0]
            colour_id = colour.get_colour(id)

            voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after = lambda e: play_queue())
            timer = FFMPEG_OPTIONS['before_options']
            timer = timer[4:15]

            global current_url, current_ctx
            current_url = list_of_songs[0]
            current_ctx = ctx
            
            time.sleep(1.5)
            started_time = time.time()
            
            if voice.is_playing():
                if '00:00:00.00' == timer:
                    client.loop.create_task(show_status(ctx, video_title, duration, id, colour_id))
                    previous_seconds = previous_minutes = previous_hours = 0
                else: 
                    client.loop.create_task(show_time(ctx, timer))
                if if_loop == False:
                    del list_of_songs[0]
                    del ctx_queue[0]
                    global embed_queue
                    embed_queue.remove_field(0)       
                
    else:
        FFMPEG_OPTIONS = {'before_options': '-ss 00:00:00.00 -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}      

@client.command()
async def play(ctx, url1 = "", url2 = "", url3 = "", url4 = "", url5 = "", url6 = ""):

    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
    global ctx_queue
    voice = get(client.voice_clients, guild = ctx.guild)

    url = url1 + url2 + url3 + url4 + url5 + url6
    print(url)

    if url == "nictuniema":
        url = "https://www.youtube.com/watch?v=ZUv_75S8gYk&ab_channel=Huberto"

    elif (validators.url(url) != 1):
        url = search_link.link(url)

    if (validators.url(url) == 1) and 'list=' in url:
        playlist = Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        for x in playlist.video_urls:
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(x, download = False)
                video_title = info.get('title', None)
                add_to_queue(x)
                add_to_embed(video_title, x, info['duration'])
                ctx_queue.append(ctx)
    else:
        with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', None)
                add_to_queue(url)
                add_to_embed(video_title, url, info['duration'])
        ctx_queue.append(ctx)

    if not ctx.guild.voice_client in client.voice_clients:
        channel = ctx.author.voice.channel
        await channel.connect()
        
    play_queue() 

@client.command()
async def pause(ctx):
    time.sleep(0.1)
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.channel.send('Song **paused** ⏸️')
    else:
        await ctx.channel.send('Nothing is playing right now!')

def get_ss_time(seconds, end):
    print(duration)
    h = int(duration / 3600)
    m = int((duration / 60) % 60)
    s = duration % 60

    ss_music_whole_time = str(datetime.time(h, m, s)) + ".00"

    global started_time
    global previous_hours, previous_minutes, previous_seconds

    current_hours = int(round(end - started_time) / 3600)
    current_minutes = int(round(end - started_time) / 60)
    current_seconds = round(end - started_time) % 60

    new_hours = previous_hours + int(seconds / 3600) + current_hours
    new_minutes = previous_minutes + int(seconds / 60) + current_minutes
    new_seconds = previous_seconds + (seconds % 60) + current_seconds

    print("Uplynelo: ", current_hours, current_minutes, current_seconds)
    print("nowe czasy: ", new_hours, new_minutes, new_seconds)

    if new_seconds >= 60:
        new_minutes += int(new_seconds / 60)
        new_seconds = (new_seconds % 60)
        if new_minutes >= 60:
            new_hours += int(new_minutes / 60)
            new_minutes = new_minutes % 60

    elif new_minutes >= 60:
        new_hours += int(new_minutes / 60)
        new_minutes = new_minutes % 60

    ss_time = str(datetime.time(new_hours, new_minutes, new_seconds)) + ".00"
    print(ss_time)
    print(ss_music_whole_time)

    if ss_music_whole_time > ss_time:
        previous_hours = new_hours
        previous_minutes = new_minutes
        previous_seconds = new_seconds
        return ss_time
    else:
        return 0

@client.command()
async def forward(ctx, seconds : int):
    time.sleep(0.1)
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing():
        end = time.time()
        ss_time = get_ss_time(seconds, end)
        global list_of_songs, ctx_queue, if_loop, current_url, current_ctx, FFMPEG_OPTIONS
        if if_loop == False and ss_time != 0:
            list_of_songs.insert(0, current_url)
            ctx_queue.insert(0, current_ctx)
            FFMPEG_OPTIONS = {'before_options': f'-ss {ss_time} -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        time.sleep(0.5)
        voice.stop()
    else:
        await ctx.channel.send("Nothing is playing right now!")

@client.command()
async def resume(ctx):
    time.sleep(0.1)
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice.is_paused():
        await ctx.channel.send('Song **resumed** ⏯️')
        voice.resume()
    else:
        await ctx.channel.send('Nothing is paused right now!')

@client.command()
async def skip(ctx):
    time.sleep(0.5)
    voice = get(client.voice_clients, guild = ctx.guild)
    if voice.is_playing():
        global FFMPEG_OPTIONS
        await ctx.channel.send('Song **skipped** ⏹️')
        voice.stop()
        FFMPEG_OPTIONS = {'before_options': '-ss 00:00:00.00 -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    else:
        await ctx.channel.send('Nothing is playing right now!')
        

@client.command()
async def clear(ctx, amount : int):
    deleted_messages = await ctx.channel.purge(limit = amount, check = lambda x: bot_prefix in x.content or bot_id == x.author.id)
    how_many = len(deleted_messages)
    await ctx.send(f"Usunieto **{how_many}** wiadomosci! ♻️", delete_after = 10)

@client.command()
async def loop(ctx):
    global if_loop
    if if_loop == False:
        if_loop = True
        await ctx.send("Loop **enabled** 🔁")
    else:
        if_loop = False
        await ctx.send("Loop **disabled** ❌")
        voice = get(client.voice_clients, guild = ctx.guild)
        if voice.is_playing and len(list_of_songs) > 0:
            del list_of_songs[0]
            del ctx_queue[0]
            global embed_queue
            embed_queue.remove_field(0)

@client.command()
async def coin(ctx):
    do_wylosowania = ('Orzeł', 'Reszka')
    await ctx.channel.send(random.choice(do_wylosowania))

# ctx - kanal na ktorym zostala wyslana wiadomosc z komenda :)
@client.command()
async def help(ctx):
    embed = discord.Embed(title = "Commands", url = "https://github.com/Resmakor", description = "powered by Resmakor", color = 0xeb1e1e)
    embed.add_field(name = f"{bot_prefix}play <nazwa>", value = "Bot wlacza muzyke i dolacza do kanalu glosowego. Jezeli juz cos gra, to dodaje do kolejki", inline = False)
    embed.add_field(name = f"{bot_prefix}pause", value = "Bot zatrzymuje piosenke", inline = False)
    embed.add_field(name = f"{bot_prefix}resume", value = "Bot wznawia piosenke", inline = False)
    embed.add_field(name = f"{bot_prefix}skip", value = "Bot pomija piosenke", inline = False)
    embed.add_field(name = f"{bot_prefix}queue", value = "Bot wyswietla status kolejki", inline = False)
    embed.add_field(name = f"{bot_prefix}loop", value = "Bot zapetla kolejny utwor az do odwolania! Odwolanie tez komenda 'loop'", inline = False)
    embed.add_field(name = f"{bot_prefix}forward <ilosc>", value = "Bot przewija piosenke o 'ilosc' sekund'", inline = False)
    embed.add_field(name = f"{bot_prefix}join", value = "Bot dolacza do kanalu glosowego", inline = False)
    embed.add_field(name = f"{bot_prefix}dc", value = "Bot opuszcza kanal glosowy", inline = False)
    embed.add_field(name = f"{bot_prefix}coin", value = "Bot rzuca moneta", inline = False)
    embed.add_field(name = f"{bot_prefix}cannon <discordmember>", value = "Bot rzuca uzytkownikiem po kanalach, pozniej wraca do swojego", inline = False)
    embed.add_field(name = f"{bot_prefix}clear <ilosc>", value = "Bot usuwa wiadomosci z komendami i swoje wlasne do <ilosc> wstecz!", inline = False)
    embed.add_field(name = f"{bot_prefix}listen <discordmember>", value = "Bot sprawdza czego ktos slucha na Spotify", inline = False)
    await ctx.send(embed=embed, delete_after = 30)


client.run(token)