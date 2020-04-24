import discord
from discord import Embed
from discord.ext import commands
import logging
import os
import traceback
import re
from datetime import datetime
from db import knowledge
from db import command_db
from random import randint
from utils import generate_random_color
from utils import generate_random_token
from utils import grouping
from info import get_help
from config import get_id
from echidna.daug import get_default_embed

id = 462810739204161537
logging.basicConfig(level=logging.INFO)
bot = commands.Bot(command_prefix=('/', f'<@{id}> ', f'<@!{id}> '), help_command=None)
token = os.environ['DISCORD_BOT_TOKEN']

ID = get_id()


@bot.event
async def on_ready():
    channel_login = bot.get_channel(id=ID.channel.login)
    await channel_login.send(str(datetime.now()))


@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.channel.TextChannel):
            return
        await parse(message)
        await bot.process_commands(message)
    except Exception as e:
        await message.channel.send(str(e))
        channel_traceback = bot.get_channel(id=ID.channel.traceback)
        message_traceback = f'```\n{traceback.format_exc()}\n```'
        await channel_traceback.send(message_traceback)


def is_developer():
    async def predicate(ctx):
        return ctx.author.id == ID.user.developer
    return commands.check(predicate)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def neko(ctx):
    await ctx.send('にゃーん')


@bot.command()
@is_developer()
async def guilds(ctx):
    for s in bot.guilds:
        is_admin = s.me.guild_permissions.administrator
        await ctx.channel.send(f'{s.name}：{is_admin}')


@bot.command()
@is_developer()
async def purge(ctx):
    while (await ctx.message.channel.purge()):
        pass


@bot.command()
@commands.has_permissions(administrator=True)
async def topic(ctx, topic):
    await ctx.channel.edit(topic=topic)


@bot.command()
async def member_status(ctx):
    text = ctx.author.voice.voice_channel.name
    await ctx.send(text)


@bot.command()
async def member(ctx):
    arg = ctx.guild.member_count
    text = f'このサーバーには{arg}人のメンバーがいます'
    await ctx.send(text)


@bot.command()
@is_developer()
async def debug_role(ctx):
    embed = Embed(title="role name", description="role id")
    for role in ctx.guild.roles:
        embed.add_field(name=role.name, value=role.id, inline=False)
    await ctx.send(embed=embed)


@bot.command()
@is_developer()
async def debug_guild(ctx):
    await ctx.send(ctx.guild.id)


@bot.command()
async def help(ctx):
    embed = get_help(bot)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def create_role(ctx, name: str):
    if name.lower() in [role.name.lower() for role in ctx.guild.roles]:
        msg = 'その役職は既に存在します'
    else:
        await ctx.guild.create_role(name=name)
        msg = f'役職 {name} を作成しました'
    await ctx.send(msg)


@bot.command()
@commands.has_permissions(administrator=True)
async def delete_role(ctx, arg):
    role_names = [role.name.lower() for role in ctx.guild.roles]
    if arg in role_names:
        index = role_names.index(arg)
        role = ctx.guild.roles[index]
        await role.delete()
        msg = f'役職 {role.name} を削除しました'
    else:
        msg = f'役職 {arg} は存在しません'
    await ctx.send(msg)


@bot.command()
async def randcolor(ctx):
    await ctx.send(str(generate_random_color()))


@bot.command()
async def randid(ctx):
    await ctx.channel.send(randint(10 ** 17, 10 ** 18 - 1))


@bot.command()
async def randtoken(ctx):
    await ctx.channel.send(generate_random_token())


@bot.command()
async def db(ctx, *args):
    msg = await command_db(ctx.message, bot)
    await ctx.send(msg)


async def parse(message):
    if re.fullmatch('/[0-9]+', message.content):
        number = int(message.content[1:])
        msg = await grouping(message, number)
        await message.channel.send(msg)
    if message.content.startswith('/echo '):
        if message.author.id == ID.user.developer:
            arg = message.content.split('/echo ')[1]
            await message.delete()
            await message.channel.send(arg)
        else:
            msg = 'コマンドを実行する権限がありません'
            await message.channel.send(msg)
    if message.content:
        if str(bot.user.id) in message.content.split()[0]:
            msg = knowledge(message)
            await message.channel.send(msg)
    if message.content.startswith('echo:'):
        await echo(message)
    if message.content.startswith('embed:'):
        await embed(message)


async def send2developer(msg):
    developer = bot.get_user(ID.user.developer)
    dm = await developer.create_dm()
    await dm.send(msg)


async def echo(message):
    await message.delete()
    n = len('echo:')
    text = message.content[n:]
    await message.channel.send(text)


async def embed(message):
    if message.author.guild_permissions.administrator:
        await message.delete()
        n = len('embed:')
        embed = get_default_embed(message.content[n:])
        await message.channel.send(embed=embed)


if __name__ == '__main__':
    bot.load_extension('jishaku')
    bot.load_extension('dispander')
    bot.load_extension('discordbotjp.cog')
    bot.load_extension('cogs.werewolf')
    bot.run(token)
