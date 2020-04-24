import os
import logging
from operator import mul
from functools import reduce
from discord.ext import commands
from datetime import datetime as dt

logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix=commands.when_mentioned_or('/'), help_command=None)


@bot.event
async def on_ready():
    ID = reduce(mul, (2, 7, 11, 33637, 223253, 434803))
    await bot.get_channel(ID).send(dt.now().strftime("%Y/%m/%d %H:%M:%S"))


if __name__ == '__main__':
    bot.load_extension('jishaku')
    bot.load_extension('dispander')
    bot.load_extension('discordbotjp.cog')
    bot.load_extension('cogs.admin')
    bot.load_extension('cogs.database')
    bot.load_extension('cogs.public')
    bot.load_extension('cogs.werewolf')
    bot.run(os.environ['DISCORD_BOT_TOKEN'])
