import string
import discord
from discord.ext import commands
from random import randint
from random import choices
from daug.utils.dpyexcept import excepter

class PublicFeaturesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @excepter
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.hybrid_command()
    @excepter
    async def neko(self, ctx):
        await ctx.send('にゃーん')

    @commands.hybrid_command()
    @excepter
    async def randcolor(self, ctx):
        """10進数のカラーコードをランダム生成します"""
        await ctx.send(str(generate_random_color()))

    @commands.hybrid_command()
    @excepter
    async def randid(self, ctx):
        """DiscordのIDのダミーを生成します"""
        await ctx.send(randint(10 ** 18, 10 ** 19 - 1))

    @commands.hybrid_command()
    @excepter
    async def randtoken(self, ctx):
        """Discordのアクセストークンのダミーを生成します"""
        await ctx.send(generate_random_token())

def get_help(bot):
    embed = discord.Embed(
        title=bot.user.name,
        url='https://github.com/1ntegrale9/discordbot-echidna',
        description='powered by discord.py',
        color=0x3a719f)
    embed.set_thumbnail(
        url=bot.user.avatar_url)
    return embed

def generate_random_token():
    length = (24, 34)
    strings = choices(string.ascii_letters + string.digits, k=sum(length))
    strings.insert(length[0], '.')
    return ''.join(strings)

def generate_random_color() -> int:
    """カラーコードを10進数で返す"""
    rgb = [randint(0, 255) for _ in range(3)]
    return int('0x{:X}{:X}{:X}'.format(*rgb), 16)

async def setup(bot):
    await bot.add_cog(PublicFeaturesCog(bot))
