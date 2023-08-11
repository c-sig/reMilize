import json
import os
import discord
import dotenv

bot = discord.Bot(intents=discord.Intents.all())
dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))


def file_check(filename, data=None):  # checks if json file exists, create it if not
    try:
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        write_file(filename, {data})


def write_file(filename, data):  # writes data to file
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command(description="Sends the bots latency.")
async def ping(ctx):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms')


bot.load_extension('cogs.permission')
bot.load_extension('cogs.series')
bot.load_extension('cogs.group')
bot.load_extension('cogs.chapter')
bot.load_extension('cogs.job')

bot.run(token)
