import discord
from discord.ext import commands
import os
import re
import redis
import traceback
from db import command_db
from random import randint, shuffle
from attrdict import AttrDict

client = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']
r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)

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
        await run_command(message)
        await expand_quote(message)
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
        await ctx.channel.send(f'{s.name}：{s.me.guild_permissions.administrator}')


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


async def run_command(message):
    msg, embed = None, None
    remark = message.content
    if re.fullmatch('/[0-9]+', remark):
        msg = await grouping(message, int(remark[1:]))
    if remark.startswith('/echo '):
        if message.author.id == ID.user.developer:
            arg = remark.split('/echo ')[1]
            await message.delete()
            await message.channel.send(arg)
        else:
            msg = 'コマンドを実行する権限がありません'
    if remark.startswith('/db '):
        msg = await command_db(r, message, client)
    elif remark.startswith(f'<@{client.user.id}>'):
        args = remark.split()
        if len(args) == 3 and args[1] == '教えて':
            key = f'{message.guild.id}:{args[2]}'
            if r.exists(key):
                msg = f'{args[2]} は {r.get(key)}'
            else:
                msg = '？'
        elif len(args) == 4 and args[1] == '覚えて':
            key = f'{message.guild.id}:{args[2]}'
            r.set(key, args[3])
            r.sadd(message.guild.id, args[2])
            msg = f'{args[2]} は {args[3]}、覚えました！'
        else:
            msg = '？'
    if msg:
        await message.channel.send(msg)
    if embed:
        await message.channel.send(embed=embed)


async def expand_quote(message):
    url_discord_message = (
        'https://discordapp.com/channels/'
        r'(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
    )
    for ID in re.finditer(url_discord_message, message.content):
        embed = await fetch_embed(ID)
        await message.channel.send(embed=embed)


async def fetch_embed(ID):
    if message.guild.id == ID['guild']:
        channel = message.guild.get_channel(ID['channel'])
        message = await channel.fetch_message(ID['message'])
        return compose_embed(message)
    else:
        return discord.Embed(title='404')


def compose_embed(message):
    embed = discord.Embed(
        description=message.content,
        timestamp=message.timestamp)
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar_url)
    embed.set_footer(
        text=message.channel.name,
        icon_url=message.guild.icon_url)
    return embed


def grouping(message, n):
    voicechannel = message.author.voice.voice_channel
    if not voicechannel:
        return 'ボイスチャンネルに入ってコマンドを入力してください'
    members = [m.mention for m in voicechannel.voice_members]
    if len(members) == 0:
        return 'ボイスチャンネルにメンバーがいません'
    shuffle(members)
    groups, g = [], []
    rest = []
    rest_number = len(members) % n
    if rest_number != 0:
        for _ in range(rest_number):
            rest.append(members.pop())
    for i, m in enumerate(members):
        if len(g) < n-1:
            g.append(m)
        else:
            g.append(m)
            tmp = ' '.join(g)
            groups.append(f'{(i+1)//n}班 {tmp}')
            g = []
    if rest:
        groups.append('余り {}'.format(' '.join(rest)))
    return '\n'.join(groups)


def is_common(role):
    if role.is_default():
        return False
    if role.managed:
        return False
    if role.permissions.kick_members:
        return False
    if role.permissions.ban_members:
        return False
    if role.permissions.administrator:
        return False
    if role.permissions.manage_channels:
        return False
    if role.permissions.manage_guild:
        return False
    if role.permissions.manage_messages:
        return False
    if role.permissions.mention_everyone:
        return False
    if role.permissions.mute_members:
        return False
    if role.permissions.deafen_members:
        return False
    if role.permissions.manage_nicknames:
        return False
    if role.permissions.manage_roles:
        return False
    if role.permissions.manage_webhooks:
        return False
    if role.permissions.manage_emojis:
        return False
    return True


def get_role_names(roles):
    return sorted([role.name for role in roles if is_common(role)])


def generate_random_color() -> int:
    """カラーコードを10進数で返す"""
    rgb = [randint(0, 255) for _ in range(3)]
    return int('0x{:X}{:X}{:X}'.format(*rgb), 16)


if __name__ == '__main__':
    client.run(token)
