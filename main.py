import os
import logging
import discord
from operator import mul
from functools import reduce
from discord.ext import commands
from datetime import datetime as dt

logging.basicConfig(level=logging.INFO)
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('/'),
    help_command=None,
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False),
)
config = {
    'Daug': {
        'guild_id': 494911447420108820,
        'guild_logs_id': 674500858054180874,
        'role_bot_limited_id': 710758653321281597,
        'role_member_id': 579591779364372511,
        'role_contributor_id': 631299456037289984,
        'role_committer_id': 704548043537645621,
        'role_staff_id': 741325667550887946,
        'role_committer_perm_id': 858642308642897921,
        'role_staff_perm_id': 834963970615934996,
        'channel_tips_id': 693388545628438538,
        'category_issues_id': 601219955035209729,
        'category_open_id': 575935336765456394,
        'category_closed_id': 640090897417240576,
        'category_archive_id': 689447835590066212,
    },
}


@bot.event
async def on_ready():
    ID = reduce(mul, (3, 3, 80071, 152837, 4318511))
    await bot.get_channel(ID).send(dt.now().strftime("%Y/%m/%d %H:%M:%S"))


if __name__ == '__main__':
    bot.config = config
    bot.load_extension('jishaku')
    bot.load_extension('Daug.extensions.channels')
    bot.load_extension('Daug.extensions.favorite')
    bot.load_extension('Daug.extensions.join')
    bot.load_extension('Daug.extensions.leave')
    bot.load_extension('Daug.extensions.thread')
    bot.load_extension('Daug.extensions.utils')
    bot.load_extension('extensions.admin')
    # bot.load_extension('extensions.database')
    bot.load_extension('extensions.prototype')
    bot.load_extension('extensions.public')
    bot.load_extension('extensions.role')
    bot.load_extension('extensions.werewolf')
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
