import math
import time
import json
import requests
from colorama import Fore
import discord, time
from discord.ext import tasks
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="+", intents=intents)

with open("config.json") as conf:
    config = json.load(conf)
    channels = config["channels"]
    bot_token = config["token"]

global owd_bans, ostaff_bans
global session

session = requests.Session()
owd_bans = None
ostaff_bans = None

session.headers.update({
    "Accept": "application/json",
    "Origin": "https://plancke.io",
    "Referer": "https://plancke.io/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
})

#Startup
@bot.event
async def on_ready():
    checkloop.start()
    print(f"{Fore.LIGHTGREEN_EX}Checker has started!{Fore.RESET}")

async def send(embed):
    for channel_id in channels:
        try:
            channel = bot.get_channel(channel_id)
            await channel.send(embed=embed)
        except Exception as e:
            print(e)
            continue

async def addChannel(channel_id):
    channels.append(channel_id)
    config = {
        "token": bot_token,
        "channels": channels
    }
    with open("config.json", "w") as f:
        f.write(json.dumps(config, indent=4))
        f.close()

async def removeChannel(channel_id):
    channels.remove(channel_id)
    config = {
        "token": bot_token,
        "channels": channels
    }
    with open("config.json", "w") as f:
        f.write(json.dumps(config, indent=4))
        f.close()

@bot.command()
async def subscribe(ctx, channel: int):
    try:
        await addChannel(channel)
        await ctx.send(f"Successfully subscribed to channel <#{channel}>!")
    except Exception as e:
        await ctx.send(f"Usage: `+subscribe <channel id>`")
        print(e)

@bot.command()
async def unsubscribe(ctx, channel: int):
    try:
        await addChannel(channel)
        await ctx.send(f"Successfully unsubscribed to channel <#{channel}>.")
    except Exception as e:
        await ctx.send(f"Usage: `+unsubscribe <channel id>`")
        print(e)

# The actual checker
@tasks.loop(seconds=0.1)
async def checkloop():
    global owd_bans, ostaff_bans, session
    resp = session.get("https://api.plancke.io/hypixel/v1/punishmentStats")
    # print(resp.text)
    wd_bans = resp.json().get("record").get("watchdog_total")
    staff_bans = resp.json().get("record").get("staff_total")
    if owd_bans != None and ostaff_bans != None:
        wban_dif = wd_bans - owd_bans
        sban_dif = staff_bans - ostaff_bans

        if wban_dif > 0:
            embed = discord.Embed(
                color=discord.Color.from_rgb(247, 57, 24),
                description=f"<t:{math.floor(time.time())}:R>",
            ).set_author(name=f"Watchdog banned {wban_dif} player{'s' if wban_dif > 1 else ''}!")
            await send(embed=embed)

        if sban_dif > 0:
            embed = discord.Embed(
                color=discord.Color.from_rgb(247, 229, 24),
                description=f"<t:{math.floor(time.time())}:R>",
            ).set_author(name=f"Staff banned {sban_dif} player{'s' if sban_dif > 1 else ''}!")
            await send(embed=embed)

    owd_bans = wd_bans
    ostaff_bans = staff_bans


bot.run(bot_token)
