import math
import time
import json
import requests
from colorama import Fore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import discord, time
from discord.ext import tasks
from discord.ext import commands

bot = commands.Bot(command_prefix="nya~", intents=discord.Intents.default())

with open("config.json") as conf:
    config = json.load(conf)
    channel_id = config["channel"]
    bot_token = config["token"]

global owd_bans, ostaff_bans
global session

session = requests.Session()
owd_bans = None
ostaff_bans = None

def getCookies():
    chromedriver_path = "chromedriver.exe"
    browser = webdriver.Chrome(chromedriver_path)
    browser.get("https://plancke.io")
    wait = WebDriverWait(browser, 15)
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"wrapper\"]/div[1]/div[2]/div")))
    time.sleep(5)
    cookies = {}
    for cookie in browser.get_cookies():
        cookies[cookie["name"]] = cookie["value"]
    browser.quit()
    print(cookies)
    session.headers.update({
        "Accept": "application/json",
        "Origin": "https://plancke.io",
        "Referer": "https://plancke.io/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    })
    session.cookies.update(cookies)

#Startup
@bot.event
async def on_ready():
    global channel
    getCookies()
    channel = bot.get_channel(channel_id)
    print(f"Logging channel set to {channel.name}")
    checkloop.start()
    print(f"{Fore.LIGHTGREEN_EX}Checker has started!{Fore.RESET}")

# The actual checker
@tasks.loop(seconds=1)
async def checkloop():
    global owd_bans, ostaff_bans, session
    resp = session.get(
        "https://api.plancke.io/hypixel/v1/punishmentStats"
    )
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
            ).set_author(name=f"Watchdog banned {wban_dif} player(s)!")
            await channel.send(embed=embed)

        if sban_dif > 0:
            embed = discord.Embed(
                color=discord.Color.from_rgb(247, 229, 24),
                description=f"<t:{math.floor(time.time())}:R>",
            ).set_author(name=f"Staff banned {sban_dif} player(s)!")
            await channel.send(embed=embed)

    owd_bans = wd_bans
    ostaff_bans = staff_bans


bot.run(bot_token)
