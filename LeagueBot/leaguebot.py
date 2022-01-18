import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

import cassiopeia as cass
from cassiopeia import Summoner, Match
from cassiopeia.data import Season, Queue
from collections import Counter

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

cass.set_riot_api_key("RGAPI-61101e6a-1d91-49c9-8ed4-c3062568ae54")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='L!')

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

@bot.command(name='summary')
async def status(ctx, Sumname):
	if Sumname is None:
		await ctx.send("Please include a valid summoner name")
	else:
		URL = "https://lolprofile.net/summoner/na/" + Sumname
		rank = requests.get(URL)
		rankSoup = BeautifulSoup(rank.content, "html.parser")
		page = rankSoup.find("div", class_="s-rs-info")
		tier = page.find("span", class_="tier")
		lp = page.find("span", class_="lp")
		wins = page.find("span", class_="win-txt")
		losses = page.find("span", class_="lose-txt")
		temp1 = wins.text.split()
		wint = int(temp1[0])
		temp2 = losses.text.split()
		lost = int(temp2[0])
		print(wint)
		print(lost)
		winRate = truncate((wint / (lost + wint)) * 100, 1)
		summoner = Summoner(name=Sumname, region="NA")
		cms = summoner.champion_masteries
		response = "Level: " + str(summoner.level) + "\n"
		response += "Highest Mastery Champion: " + cms[0].champion.name + "\n"
		response += "Rank: " + tier.text + " " + lp.text + "\n"
		response += wins.text + " / " + losses.text + "\n"
		response += "Winrate: " + str(winRate) + "%\n"
		if cms[0].points < 1000:
			response += "Highest Mastery Points: " + str(cms[0].points) + "\n"
		elif cms[0].points >= 1000:
			formatted = "{:,}".format(cms[0].points)
			response += "Highest Mastery Points: " + formatted + "\n"

		embed = discord.Embed(title = "Summoner Summary", description=response, color=discord.Color.blue())
		embed.set_author(name=summoner.name, url="https://u.gg/lol/profile/na1/" + summoner.name + "/overview", icon_url=ctx.author.avatar_url)
		embed.set_thumbnail(url=summoner.profile_icon.url)
		await ctx.send(embed=embed)

@bot.command(name='match')
async def status(ctx, Sumname):
	summoner = Summoner(name=Sumname, region="NA")

	mh = cass.get_match_history(continent=summoner.region.continent, puuid=summoner.puuid, queue=Queue.ranked_solo_fives)
	champion_id_to_name_mapping = {champion.id: champion.name for champion in cass.get_champions(region="NA")}

	match = mh[0]
	p = match.participants[summoner]
	champion = champion_id_to_name_mapping[p.champion.id]
	index = champion.find("'")

	if index != -1:
		champion = champion[0:index] + champion[index+1:len(champion)]
	else:
		index = champion.find(".")
		if index != -1:
			champion = champion[0:index] + champion[index+1:len(champion)-1]

	blue = False
	for p in match.blue_team.participants:
		if p.summoner.name == summoner.name:
			blue = True
			break
	blueWin = match.blue_team.win

	kills = p.stats.kills
	deaths = p.stats.deaths
	assists = p.stats.assists
	KDA = str(kills) + "/" + str(deaths) + "/" + str(assists)
	ratio = truncate(((kills + assists) / deaths), 2)

	response = champion

	if blue and blueWin:
		embed = discord.Embed(title = "Victory", description=response, color=discord.Color.blue())
	elif not blue and not blueWin:
		embed = discord.Embed(title = "Victory", description=response, color=discord.Color.blue())
	else:
		embed = discord.Embed(title = "Defeat", description=response, color=discord.Color.red())

	embed.set_author(name="Latest Match")
	embed.add_field(name="Score", value=KDA + "\n**" + str(ratio) + "**", inline=False)
	embed.set_image(url="http://ddragon.leagueoflegends.com/cdn/img/champion/splash/" + champion + "_0.jpg")
	embed.set_thumbnail(url=summoner.profile_icon.url)
	await ctx.send(embed=embed)


bot.run(TOKEN)