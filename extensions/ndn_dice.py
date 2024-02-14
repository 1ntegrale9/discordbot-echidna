import discord
from discord.ext import commands
from daug.utils.dpyexcept import excepter
from random import randint
import re

ndnpattern = re.compile(r'(\d+)d(\d+)')


class NDNDiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        match = ndnpattern.fullmatch(message.content)
        if match is None:
            return
        m, n = map(int, match.groups())
        if m > 100 or n > 10000:
            await message.reply('10000面100回(100d10000)以上は対応していません。')
            return
        rolls = [randint(1, n) for _ in range(m)]
        roll_sum = sum(rolls)
        results = [
            f'{n}面ダイスを{m}回振りました',
            f'出目: {", ".join(str(x) for x in rolls)}',
            f'合計: {roll_sum}',
        ]
        response = '\n'.join(results)
        await message.reply(response)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(NDNDiceCog(bot))
