from functools import wraps
from datetime import datetime
import discord
from discord.ext import commands
from constant import CHANNEL_LOG_SYSTEM_ID

def dpylogger(func, *, _channel_id=None):
    @wraps(func)
    async def wrapped(self, *args, **kwargs):
        channel_id = _channel_id or CHANNEL_LOG_SYSTEM_ID
        if len(args) >= 1 and isinstance(args[0], discord.Interaction):
            interaction: discord.Interaction = args[0]
            channel = interaction.client.get_channel(channel_id)
        else:
            bot: commands.Bot = self.bot
            channel = bot.get_channel(channel_id)

        if channel:
            content = ' '.join((self.__class__.__name__, func.__name__, datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')))
            await channel.send(content)
        await func(self, *args, **kwargs)
    return wrapped
