import discord
from discord.ext import commands
import os
import re
import redis
import traceback
from db import command_db
from random import randint, shuffle

client = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']
r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
DEVELOPER = discord.User(id='314387921757143040')
QUOTE_URL_BASE = 'https://discordapp.com/channels/'


@client.event
async def on_ready():
    await client.send_message(
        client.get_channel('502837677108887582'),
        'ログインしました'
        )


@client.event
async def on_message(message):
    try:
        if message.author != client.user:
            await run_command(r, client, message)
            await expand_quote(client, message)
            await client.process_commands(message)
    except Exception as e:
        await client.send_message(message.channel, str(e))
        await client.send_message(
            client.get_channel('502901411445735435'),
            f'```\n{traceback.format_exc()}\n```'
            )


@client.command()
async def ping(ctx):
    await ctx.send('pong')


@client.command()
async def neko(ctx):
    await ctx.send('にゃーん')


@client.command()
async def info(ctx):
    for s in client.servers:
        await ctx.channel.send(f'{s.name}：{s.me.server_permissions.administrator}')


@client.command()
async def clear(ctx):
    if ctx.author == DEVELOPER:
        clearflag = True
        while (clearflag):
            logs = [log async for log in client.logs_from(ctx.channel)]
            if len(logs) > 2:
                await client.delete_messages(logs)
            else:
                clearflag = False
    else:
        await ctx.send('コマンドを実行する権限がありません')


@client.command()
async def role(ctx):
    role_names = get_role_names(ctx.guild.roles, is_common)
    text = 'このサーバーにある役職は以下の通りです\n' + \
        ', '.join(role_names) if role_names else '役職がありません'
    await ctx.send(text)


@client.command()
async def role_self(ctx):
    role_names = get_role_names(ctx.author.roles, is_common)
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
async def debug_server(ctx):
    await ctx.send(ctx.guild.id)


@client.command()
async def help(ctx):
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
async def create_role(ctx, arg: str):
    if arg.lower() in [role.name.lower() for role in ctx.guild.roles]:
        return 'その役職は既に存在します'
    await client.create_role(
        ctx.guild,
        name=arg,
        mentionable=True,
        color=discord.Colour(generate_random_color()),
    )
    return f'役職 {arg} を作成しました'


@client.command()
@commands.has_permissions(administrator=True)
async def delete_role(ctx, arg):
    role_names = [role.name.lower() for role in ctx.guild.roles]
    if arg in role_names:
        index = role_names.index(arg)
        role = ctx.guild.roles[index]
        await client.delete_role(ctx.guild, role)
        return f'役職 {role.name} を削除しました'
    return f'役職 {arg} は存在しません'


@client.command()
async def randcolor(ctx):
    await ctx.send(str(generate_random_color()))


async def run_command(r, client, message):
    msg, reply, no_reply, embed = None, None, None, None
    remark = message.content
    if re.fullmatch('/[0-9]+', remark):
        no_reply = await grouping(message, int(remark[1:]))
    if remark.startswith('/echo '):
        if message.author == DEVELOPER:
            arg = remark.split('/echo ')[1]
            await client.delete_message(message)
            await client.send_message(message.channel, arg)
        else:
            msg = 'コマンドを実行する権限がありません'
    if remark.startswith('/role '):
        msg = await set_roles(client, message)
    if remark.startswith('/db '):
        reply = await command_db(r, message, client)
    elif remark.startswith(f'<@{client.user.id}>'):
        args = remark.split()
        if len(args) == 3 and args[1] == '教えて':
            key = f'{message.server.id}:{args[2]}'
            if r.exists(key):
                reply = f'{args[2]} は {r.get(key)}'
            else:
                reply = '？'
        elif len(args) == 4 and args[1] == '覚えて':
            key = f'{message.server.id}:{args[2]}'
            r.set(key, args[3])
            r.sadd(message.server.id, args[2])
            reply = f'{args[2]} は {args[3]}、覚えました！'
        else:
            reply = '？'
    if msg:
        mention = str(message.author.mention) + ' '
        await client.send_message(message.channel, mention + msg)
    if reply:
        mention = str(message.author.mention) + ' '
        await client.send_message(message.channel, mention + reply)
    if no_reply:
        await client.send_message(message.channel, no_reply)
    if embed:
        await client.send_message(
            message.channel,
            message.author.mention,
            embed=embed
        )


async def expand_quote(client, msg):
    for url in get_urls(msg.content):
        embed = await discordurl2embed(client, msg.server, url)
        await client.send_message(msg.channel, embed=embed)


def compose_embed(channel, message):
    embed = discord.Embed(
        description=message.content,
        timestamp=message.timestamp)
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar_url)
    embed.set_footer(
        text=message.channel.name,
        icon_url=message.server.icon_url)
    return embed


def get_urls(text):
    pattern = QUOTE_URL_BASE + '[0-9]{18}/[0-9]{18}/[0-9]{18}'
    return re.findall(pattern, text)


async def discordurl2embed(client, server, url):
    s_id, c_id, m_id = url.split(QUOTE_URL_BASE)[1].split('/')
    if server.id == s_id:
        channel = server.get_channel(c_id)
        message = await client.get_message(channel, m_id)
        return compose_embed(channel, message)
    else:
        return discord.Embed(title='404')


async def grouping(message, n):
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
    if role.is_everyone:
        return False
    if role.managed:
        return False
    if role.permissions.administrator:
        return False
    return True


def get_role_names(roles, requirements):
    return sorted([r.name for r in roles if requirements(r)])


def generate_random_color() -> int:
    """カラーコードを10進数で返す"""
    rgb = [randint(0, 255) for _ in range(3)]
    return int('0x{:X}{:X}{:X}'.format(*rgb), 16)


async def set_roles(client, message):
    add, rm, pd, nt = [], [], [], []
    role_names = [role.name.lower() for role in message.server.roles]
    for role_name in message.content.split()[1:]:
        if role_name.lower() in role_names:
            index = role_names.index(role_name.lower())
            role = message.server.roles[index]
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
        await client.add_roles(message.author, *add)
        msg = msg + '\n役職 {} を付与しました'.format(', '.join([r.name for r in add]))
    if rm:
        await client.remove_roles(message.author, *rm)
        msg = msg + '\n役職 {} を解除しました'.format(', '.join([r.name for r in rm]))
    if pd:
        msg = msg + '\n役職 {} は追加できません'.format(', '.join([r.name for r in pd]))
    if nt:
        msg = msg + '\n役職 {} は存在しません'.format(', '.join(nt))
    return msg


if __name__ == '__main__':
    client.run(token)
