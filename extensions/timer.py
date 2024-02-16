import discord
from discord.ext import commands
from daug.utils.dpyexcept import excepter
import asyncio
import re
import time

CHANNEL_LOG_TIMER_ID = 1207452141917048832

seconds_pattern = re.compile(r'\d+秒')
minutes_pattern = re.compile(r'\d+分')
seconds_countdown_pattern = re.compile(r'\d+秒(!|！)')
minutes_countdown_pattern = re.compile(r'\d+分(!|！)')


class TimerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    @excepter
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if seconds_pattern.fullmatch(message.content):
            await self.bot.get_channel(CHANNEL_LOG_TIMER_ID).send(f'タイマー {message.guild.id} {message.content}')
            seconds = int(message.content.split('秒')[0])
            if seconds > 10 * 60:
                await message.reply('10分以内の計測が可能です', delete_after=10)
                return
            await message.reply(f'{seconds}秒測ります（計測終了:<t:{int(time.time()) + seconds + 1}:R>）')
            await asyncio.sleep(seconds)
            await message.channel.send(f'{seconds}秒が経過しました {message.author.mention}')
        if minutes_pattern.fullmatch(message.content):
            await self.bot.get_channel(CHANNEL_LOG_TIMER_ID).send(f'タイマー {message.guild.id} {message.content}')
            minutes = int(message.content.split('分')[0])
            if minutes > 10:
                await message.reply('10分以内の計測が可能です', delete_after=10)
                return
            await message.reply(f'{minutes}分測ります（計測終了:<t:{int(time.time()) + 60 * minutes + 1}:R>）')
            await asyncio.sleep(minutes * 60)
            await message.channel.send(f'{minutes}分が経過しました {message.author.mention}')
        if seconds_countdown_pattern.fullmatch(message.content):
            seconds = int(message.content.split('秒')[0])
            time_str = f'{seconds}秒'
            if seconds > 10 * 60:
                await message.reply('10分以内の計測が可能です', delete_after=10)
                return
            await message.reply(f'{time_str}測ります')
            if seconds > 30:
                await asyncio.sleep(seconds - 30)
                seconds = 30
                await message.channel.send(f'残り30秒です {message.author.mention}')
            if seconds > 10:
                await asyncio.sleep(seconds - 10)
                seconds = 10
                await message.channel.send(f'残り10秒です {message.author.mention}')
            await asyncio.sleep(seconds)
            await message.channel.send(f'{time_str}が経過しました {message.author.mention}')
        if minutes_countdown_pattern.fullmatch(message.content):
            minutes = int(message.content.split('分')[0])
            if minutes > 10:
                await message.reply('10分以内の計測が可能です', delete_after=10)
                return
            time_str = f'{minutes}分'
            await message.reply(f'{time_str}測ります')
            while minutes > 1:
                await asyncio.sleep(60)
                minutes -= 1
                await message.channel.send(f'残り{minutes}分です {message.author.mention}')
            await asyncio.sleep(30)
            await message.channel.send(f'残り30秒です {message.author.mention}')
            await asyncio.sleep(20)
            await message.channel.send(f'残り10秒です {message.author.mention}')
            await asyncio.sleep(10)
            await message.channel.send(f'{time_str}が経過しました {message.author.mention}')


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(TimerCog(bot))
