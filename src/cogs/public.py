import re
import string
from discord import Embed
from discord.ext import commands
from random import randint
from random import choices
from random import shuffle


class PublicFeatures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        await ctx.send(embed=get_help(self.bot))

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def neko(self, ctx):
        await ctx.send('にゃーん')

    @commands.command()
    async def randcolor(self, ctx):
        await ctx.send(str(generate_random_color()))

    @commands.command()
    async def randid(self, ctx):
        await ctx.channel.send(randint(10 ** 17, 10 ** 18 - 1))

    @commands.command()
    async def randtoken(self, ctx):
        await ctx.channel.send(generate_random_token())

    @commands.command()
    @commands.guild_only()
    async def member(self, ctx):
        await ctx.send(f'このサーバーには{ctx.guild.member_count}人のメンバーがいます')

    @commands.Cog.listener()
    async def on_message(self, message):
        if re.fullmatch('/[0-9]+', message.content):
            await grouping(message, int(message.content[1:]))


helps = {
    '/randid':
        'DiscordのIDのダミーを生成します',
    '/randtoken':
        'Discordのアクセストークンのダミーを生成します',
    '/randcolor':
        '10進数のカラーコードをランダム生成します',
    '/role':
        'サーバーの役職一覧を表示します',
    '/member':
        'サーバーの人数を表示します',
    '/help':
        'コマンドの一覧と詳細を表示します',
}


def get_help(bot):
    embed = Embed(
        title=bot.user.name,
        url='https://github.com/1ntegrale9/discordbot',
        description='powered by discord.py',
        color=0x3a719f)
    embed.set_thumbnail(
        url=bot.user.avatar_url)
    for k, v in helps.items():
        embed.add_field(name=k, value=v, inline=False)
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


async def grouping(message, n):
    voicechannel = message.author.voice.voice_channel
    if not voicechannel:
        return await message.channel.send('ボイスチャンネルに入ってコマンドを入力してください')
    members = [m.mention for m in voicechannel.voice_members]
    if len(members) == 0:
        return await message.channel.send('ボイスチャンネルにメンバーがいません')
    shuffle(members)
    groups, g = [], []
    rest = []
    rest_number = len(members) % n
    if rest_number != 0:
        for _ in range(rest_number):
            rest.append(members.pop())
    for i, m in enumerate(members):
        if len(g) < n - 1:
            g.append(m)
        else:
            g.append(m)
            tmp = ' '.join(g)
            groups.append(f'{(i+1)//n}班 {tmp}')
            g = []
    if rest:
        groups.append('余り {}'.format(' '.join(rest)))
    await message.channel.send('\n'.join(groups))


def setup(bot):
    bot.add_cog(PublicFeatures(bot))
