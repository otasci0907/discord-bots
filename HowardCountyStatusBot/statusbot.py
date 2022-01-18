import requests
from bs4 import BeautifulSoup

import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

URL1 = "https://status.hcpss.org/"
status = requests.get(URL1)

URL2 = "https://covid.hcpss.org/"
covid = requests.get(URL2)

statusSoup = BeautifulSoup(status.content, "html.parser")
covidSoup = BeautifulSoup(covid.content, "html.parser")

results = statusSoup.find(id="status-block")
div = results.find("div")
header = div.find("h2")
codeElement = header.find("span", class_ = "status-code")

table = covidSoup.find("table", class_= "covid-summary")
tfoot = table.find("tfoot")
td = tfoot.find_all("td")
elementary = td[0].text
middle = td[1].text
high = td[2].text

bot = commands.Bot(command_prefix='!')

@bot.command(name='status')
async def status(ctx):
	response = codeElement.text
	if codeElement.text == "Code Red":
		response = "@everyone Code Red - Schools and Offices Closed for Everyone"
	elif codeElement.text == "Code Orange":
		response += "@everyone Code Orange - Schools and Offices Closed for Students only"
	elif codeElement.text == "Code Yellow":
		response += " - Schools Early Dismissal"
	elif codeElement.text == "Code Blue":
		response += " - Schools open two hours late"
	else:
		response += " - Normal Operations"
	await ctx.send(response)

@bot.command(name='covid')
async def status(ctx, args = None):
	response = "In the last seven days there have been "
	if args == "high":
		response += high + " high school cases"
	elif args == "middle":
		response += middle + " middle school cases"
	elif args == "elementary":
		response += elementary + " elementary school cases"
	else:
		response = "Please use the format \"!covid (elementary/middle/high)\""
	await ctx.send(response)

bot.run(TOKEN)
