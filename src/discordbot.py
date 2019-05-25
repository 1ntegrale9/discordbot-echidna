import discord
from discord.ext import commands
import os
import traceback
import re
from db import knowledge
from db import command_db
from attrdict import AttrDict
from quote import expand
from utils import get_role_names
from utils import generate_random_color
from utils import grouping

client = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']

ID = AttrDict({
    'user': {
        'developer': 314387921757143040,
    },
    'channel': {
        'login': 502837677108887582,
        'debug': 577028884944388107,
        'traceback': 502901411445735435,
    },
    'category': {
        'musicbot': 548752809965781013,
    },
    'guild': {
        'bot': 494911447420108820,
    },
})


@client.event
async def on_ready():
    channel_login = client.get_channel(id=ID.channel.login)
    await channel_login.send('ログインしました')


@client.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        await parse(message)
        await client.process_commands(message)
    except Exception as e:
        await message.channel.send(str(e))
        channel_traceback = client.get_channel(id=ID.channel.traceback)
        message_traceback = f'```\n{traceback.format_exc()}\n```'
        await channel_traceback.send(message_traceback)


@client.command()
async def ping(ctx):
    await ctx.send('pong')


@client.command()
async def neko(ctx):
    await ctx.send('にゃーん')


@client.command()
async def info(ctx):
    for s in client.guilds:
        is_admin = s.me.guild_permissions.administrator
        await ctx.channel.send(f'{s.name}：{is_admin}')


@client.command()
async def clear(ctx):
    if ctx.author.id == ID.user.developer:
        while (await ctx.message.channel.purge()):
            pass
    else:
        await ctx.send('コマンドを実行する権限がありません')


@client.command()
async def role(ctx, *args):
    async def set_roles(message):
        add, rm, pd, nt = [], [], [], []
        role_names = [role.name.lower() for role in message.guild.roles]
        for role_name in message.content.split()[1:]:
            if role_name.lower() in role_names:
                index = role_names.index(role_name.lower())
                role = message.guild.roles[index]
                if role in message.author.roles:
                    rm.append(role)
                elif role.permissions.administrator:
                    pd.append(role)
                else:
                    add.append(role)
            else:
                nt.append(role_name)
        msg = ''
        if add:
            await message.author.add_roles(*add)
            rolenames = ', '.join([r.name for r in add])
            msg = f'{msg}\n役職 {rolenames} を付与しました'
        if rm:
            await message.authorr.emove_roles(*rm)
            rolenames = ', '.join([r.name for r in rm])
            msg = f'{msg}\n役職 {rolenames} を解除しました'
        if pd:
            rolenames = ', '.join([r.name for r in pd])
            msg = f'{msg}\n役職 {rolenames} は追加できません'
        if nt:
            rolenames = (', '.join(nt))
            msg = f'{msg}\n役職 {rolenames} は存在しません'
        return msg
    if args:
        msg = await set_roles(ctx.message)
        await ctx.send(msg)
    else:
        role_names = get_role_names(ctx.guild.roles)
        text = 'このサーバーにある役職は以下の通りです\n' + \
            ', '.join(role_names) if role_names else '役職がありません'
        await ctx.send(text)


@client.command()
async def role_self(ctx):
    role_names = get_role_names(ctx.author.roles)
    text = ', '.join(role_names) if role_names else '役職が設定されていません'
    await ctx.send(text)


@client.command()
async def member_status(ctx):
    text = ctx.author.voice.voice_channel.name
    await ctx.send(text)


@client.command()
async def member(ctx):
    arg = ctx.guild.member_count
    text = f'このサーバーには{arg}人のメンバーがいます'
    await ctx.send(text)


@client.command()
async def debug_role(ctx):
    embed = discord.Embed(title="role name", description="role id")
    for role in ctx.guild.roles:
        embed.add_field(name=role.name, value=role.id, inline=False)
    await ctx.send(embed=embed)


@client.command()
async def debug_guild(ctx):
    await ctx.send(ctx.guild.id)


@client.command()
async def myhelp(ctx):
    helps = {
        '`/role`':
            'サーバーの役職一覧を教えます',
        '`/role ROLENAME(s)`':
            '指定した(空白区切り複数の)役職を付与/解除します',
        '`/create_role ROLENAME`':
            '指定した役職を作成します(管理者のみ)',
        '`/delete_role ROLENAME`':
            '指定した役職を削除します(管理者のみ)',
        '`/member`':
            'サーバーのメンバー人数を教えます',
        '`/help`':
            'コマンドの一覧と詳細を表示します',
    }
    embed = discord.Embed(
        title=client.user.name,
        url='https://github.com/1ntegrale9/discordbot',
        description='discord bot w/ discord.py',
        color=0x3a719f)
    embed.set_thumbnail(
        url=client.user.avatar_url)
    for k, v in helps.items():
        embed.add_field(name=k, value=v, inline=False)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(administrator=True)
async def create_role(ctx, name: str):
    if name.lower() in [role.name.lower() for role in ctx.guild.roles]:
        return 'その役職は既に存在します'
    await ctx.guild.create_role(name=name)
    return f'役職 {name} を作成しました'


@client.command()
@commands.has_permissions(administrator=True)
async def delete_role(ctx, arg):
    role_names = [role.name.lower() for role in ctx.guild.roles]
    if arg in role_names:
        index = role_names.index(arg)
        role = ctx.guild.roles[index]
        await role.delete()
        return f'役職 {role.name} を削除しました'
    return f'役職 {arg} は存在しません'


@client.command()
async def randcolor(ctx):
    await ctx.send(str(generate_random_color()))


@client.command()
async def db(ctx, *args):
    msg = await command_db(ctx.message, client)
    await ctx.send(msg)


async def parse(message):
    await expand(message)
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
    if str(client.user.id) in message.content.split()[0]:
        msg = knowledge(message)
        await message.channel.send(msg)


if __name__ == '__main__':
    client.run(token)
