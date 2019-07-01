import discord
from discord import Embed
from discord.ext import commands
import os
import traceback
import re
import info
from datetime import datetime
from db import knowledge
from db import command_db
from random import randint
from quote import expand
from quote import compose_embed
from utils import get_role_names
from utils import generate_random_color
from utils import generate_random_token
from utils import grouping
from info import get_help
from config import get_id

client = commands.Bot(command_prefix='/', help_command=None)
token = os.environ['DISCORD_BOT_TOKEN']

ID = get_id()


def get_default_embed(description):
    return Embed.from_dict({
        'description': description,
        'color': discord.Colour.blue().value,
    })


@client.event
async def on_ready():
    channel_login = client.get_channel(id=ID.channel.login)
    await channel_login.send(str(datetime.now()))


@client.event
async def on_member_join(member):
    if member.bot:
        return
    if member.guild.id == ID.guild.bot:
        role = discord.utils.find(
            lambda r: r.name == 'member', member.guild.roles
        )
        await member.add_roles(role)


@client.event
async def on_raw_reaction_add(payload):
    user = client.get_user(payload.user_id)
    if user.bot:
        return
    channel = client.get_channel(payload.channel_id)
    if channel.category_id != ID.category.issues:
        return
    if channel.id == ID.channel.question:
        return
    if payload.emoji.name == '✅':
        await channel.edit(
            category=client.get_channel(ID.category.closed)
        )


@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    async def toggle_channel_readable(channel, can_read):
        await discord.utils.get(
            iterable=member.guild.text_channels,
            name=channel.name
        ).set_permissions(
            target=member,
            read_messages=can_read
        )
    b, a = before.channel, after.channel
    if ((b is None) ^ (a is None)
            and (b or a).category_id == ID.category.musicbot):
        await toggle_channel_readable(
            channel=(b or a),
            can_read=bool(a)
        )


@client.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        if isinstance(message.channel, discord.channel.TextChannel):
            return
        await parse(message)
        await client.process_commands(message)
    except Exception as e:
        await message.channel.send(str(e))
        channel_traceback = client.get_channel(id=ID.channel.traceback)
        message_traceback = f'```\n{traceback.format_exc()}\n```'
        await channel_traceback.send(message_traceback)


def is_developer():
    async def predicate(ctx):
        return ctx.author.id == ID.user.developer
    return commands.check(predicate)


@client.command()
async def ping(ctx):
    await ctx.send('pong')


@client.command()
async def neko(ctx):
    await ctx.send('にゃーん')


@client.command()
@is_developer()
async def guilds(ctx):
    for s in client.guilds:
        is_admin = s.me.guild_permissions.administrator
        await ctx.channel.send(f'{s.name}：{is_admin}')


@client.command()
@is_developer()
async def purge(ctx):
    while (await ctx.message.channel.purge()):
        pass


@client.command()
@commands.has_permissions(administrator=True)
async def name(ctx, name):
    await ctx.channel.edit(name=name)


@client.command()
@commands.has_permissions(administrator=True)
async def topic(ctx, topic):
    await ctx.channel.edit(topic=topic)


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
            await message.author.remove_roles(*rm)
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
@is_developer()
async def debug_role(ctx):
    embed = Embed(title="role name", description="role id")
    for role in ctx.guild.roles:
        embed.add_field(name=role.name, value=role.id, inline=False)
    await ctx.send(embed=embed)


@client.command()
@is_developer()
async def debug_guild(ctx):
    await ctx.send(ctx.guild.id)


@client.command()
async def help(ctx):
    embed = await info.get_help(client)
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
async def randid(ctx):
    await ctx.channel.send(randint(10 ** 17, 10 ** 18 - 1))


@client.command()
async def randtoken(ctx):
    await ctx.channel.send(generate_random_token())


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
    if message.content:
        if str(client.user.id) in message.content.split()[0]:
            msg = knowledge(message)
            if msg == '？':
                await message.channel.send(embed=get_help(client))
            else:
                await message.channel.send(msg)
        if message.content.split()[0] == '招待':
            await join(message)
        if message.content.split()[0] == '追放':
            await leave(message)
    if message.content.startswith('name:'):
        await rename(message)
    if message.content.startswith('new:'):
        await create_channel(message)
    if message.content.startswith('private:'):
        await create_private_channel(message)
    if message.content.startswith('topic:'):
        await overwrite_topic(message)
    if message.content.startswith('echo:'):
        await echo(message)
    if message.content.startswith('embed:'):
        await embed(message)
    if message.channel.id == ID.channel.question:
        await qa_thread(message)
    await age(message)


async def send2developer(msg):
    developer = client.get_user(ID.user.developer)
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


async def join(message):
    members = message.mentions
    if not bool(members):
        await message.channel.send('誰を招待すればいいの？')
        return
    channel = message.channel_mentions
    if len(channel) == 0:
        channel = message.channel
    elif len(channel) == 1:
        channel = channel[0]
        if not message.author.permissions_in(channel).read_messages:
            await message.channel.send('君には招待する権利がないみたい')
            return
    else:
        await message.channel.send('チャンネルを1つだけ指定してね！')
        return
    for member in members:
        await channel.set_permissions(member, read_messages=True)
        description = f'{member.mention} を招待したよ'
        embed = get_default_embed(description)
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)


async def leave(message):
    members = message.mentions
    if not bool(members):
        await message.channel.send('誰を追放すればいいの？')
        return
    for member in members:
        await message.channel.set_permissions(member, read_messages=False)
        description = f'{member.mention} を追放したよ'
        embed = get_default_embed(description)
        embed.set_thumbnail(url=member.avatar_url)
        await message.channel.send(embed=embed)


async def age(message):
    category = message.channel.category
    if category.id == ID.category.free:
        await message.channel.edit(
            category=category,
            position=0
        )


async def create_channel(message):
    if message.guild.id != ID.guild.werewolf:
        return
    n = len('new:')
    await message.guild.create_text_channel(
        name=message.content[n:],
        category=message.guild.get_channel(ID.category.free)
    )


async def create_private_channel(message):
    if message.guild.id != ID.guild.werewolf:
        return
    n = len('private:')
    await message.guild.create_text_channel(
        name=message.content[n:],
        category=message.guild.get_channel(ID.category.private),
        overwrites={
            message.guild.default_role: discord.PermissionOverwrite(
                read_messages=False
            ),
            message.author: discord.PermissionOverwrite(read_messages=True),
        }
    )


async def rename(message):
    if message.channel.id == ID.channel.question:
        return
    can_rename_categories = (
        ID.category.private,
        ID.category.free,
        ID.category.issues,
        ID.category.closed,
    )
    if message.channel.category_id in can_rename_categories:
        n = len('name:')
        await message.channel.edit(name=message.content[n:])
        await message.delete()


async def overwrite_topic(message):
    if message.channel.id == ID.channel.question:
        return
    can_overwrite_topic_categories = (
        ID.category.private,
        ID.category.free,
        ID.category.issues,
        ID.category.closed,
    )
    if message.channel.category_id in can_overwrite_topic_categories:
        n = len('topic:')
        await message.channel.edit(topic=message.content[n:])
        await message.delete()


async def qa_thread(message):
    category_qa = message.guild.get_channel(ID.category.issues)
    category_resolved = message.guild.get_channel(ID.category.closed)
    count = sum((
        len(category_qa.text_channels),
        len(category_resolved.text_channels)
    ))
    payload = {
        'name': f'q{count}',
        'category': category_qa,
        'slowmode_delay': 5,
    }
    channel_qa = await message.guild.create_text_channel(**payload)
    await channel_qa.edit(position=0)
    await message.guild.get_channel(ID.channel.question).edit(position=0)
    await channel_qa.send(embed=compose_embed(message))
    embed = get_default_embed(
        f'スレッド {channel_qa.mention} を作成しました {message.author.mention}'
    )
    await message.channel.send(embed=embed)


if __name__ == '__main__':
    client.run(token)
