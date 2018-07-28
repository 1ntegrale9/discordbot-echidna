from discord.message import Message
from discord.role import Role
from discord.embeds import Embed
from discord import Client
from typing import Callable, List
from random import randint, shuffle
import discord


async def run_command(client: Client, message: Message) -> None:
    """コマンドを実行する"""
    msg, no_reply, embed = None, None, None
    remark = message.content
    if remark == '/ping':
        msg = 'pong'
    if remark == '/2':
        no_reply = await grouping(message, 2)
    if remark == '/4':
        no_reply = await grouping(message, 4)
    if remark == '/role':
        role_names = get_role_names(message.server.roles, is_common)
        msg = 'このサーバーにある役職は以下の通りです\n' + \
            ', '.join(role_names) if role_names else '役職がありません'
    if remark.startswith('/echo '):
        if message.author == discord.User(id='314387921757143040'):
            arg = remark.split('/echo ')[1]
            await client.delete_message(message)
            await client.send_message(message.channel, arg)
        else:
            msg = 'コマンドを実行する権限がありません'
    if remark.startswith('/role '):
        msg = await set_roles(client, message)
    if remark == '/role_self':
        role_names = get_role_names(message.author.roles, is_common)
        msg = ', '.join(role_names) if role_names else '役職が設定されていません'
    if remark == '/member_status':
        msg = member_status(message)
    if remark.startswith('/create_role '):
        msg = await requires_admin(client, message, create_role)
    if remark.startswith('/delete_role '):
        msg = await requires_admin(client, message, delete_role)
    if remark == '/member':
        arg = message.server.member_count
        msg = f'このサーバーには{arg}人のメンバーがいます'
    if remark == '/debug_role':
        embed = discord.Embed(title="role name", description="role id")
        for role in message.server.roles:
            embed.add_field(name=role.name, value=role.id, inline=False)
    if remark == '/debug_server':
        msg = message.server.id
    if remark == '/debug_on':
        msg = toggle_debug_mode(True)
    if remark == '/debug_off':
        msg = toggle_debug_mode(False)
    if remark == '/help':
        embed = get_help(client)
    if msg:
        mention = str(message.author.mention) + ' '
        await client.send_message(message.channel, mention + msg)
    if no_reply:
        await client.send_message(message.channel, no_reply)
    if embed:
        await client.send_message(
            message.channel,
            message.author.mention,
            embed=embed
        )


async def grouping(message: Message, n: int) -> str:
    """ボイスチャットメンバーを班分けする"""
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


async def requires_admin(
        client: Client, message: Message, func: Callable) -> str:
    """管理者のみ関数を実行する"""
    if message.author.server_permissions.administrator:
        return await func(client, message)
    return '実行する権限がありません'


def toggle_debug_mode(mode: bool) -> str:
    """デバッグモードのON/OFFを切り替える"""
    global debug_mode
    debug_mode = mode
    return 'デバッグモードを{}にしました'.format('ON' if mode else 'OFF')


def is_common(role: Role) -> bool:
    """役職の権限が通常かどうかをチェックする"""
    if role.is_everyone:
        return False
    if role.managed:
        return False
    if role.permissions.administrator:
        return False
    return True


def member_status(message: Message) -> str:
    """メンバーが入っているボイスチャンネル名を返す"""
    return message.author.voice.voice_channel.name


def get_role_names(roles: List[Role], requirements: Callable) -> List[str]:
    """役職名の一覧を返す"""
    return [r.name for r in roles if requirements(r)]


def generate_random_color() -> int:
    """カラーコードを10進数で返す"""
    rgb = [randint(0, 255) for _ in range(3)]
    return int('0x{:X}{:X}{:X}'.format(*rgb), 16)


async def set_roles(client: Client, message: Message) -> str:
    """指定された役職を付与する"""
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


def get_help(client: Client) -> Embed:
    """コマンドの一覧と詳細をembedで返す"""
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
    return embed


async def create_role(client: Client, message: Message) -> str:
    """役職を作成する"""
    arg = message.content.split('/create_role ')[1]
    if arg.lower() in [role.name.lower() for role in message.server.roles]:
        return 'その役職は既に存在します'
    await client.create_role(
        message.server,
        name=arg,
        mentionable=True,
        color=discord.Colour(generate_random_color()),
    )
    return f'役職 {arg} を作成しました'


async def delete_role(client: Client, message: Message) -> str:
    """役職を削除する"""
    arg = message.content.split('/delete_role ')[1].lower()
    role_names = [role.name.lower() for role in message.server.roles]
    if arg in role_names:
        index = role_names.index(arg)
        role = message.server.roles[index]
        await client.delete_role(message.server, role)
        return f'役職 {role.name} を削除しました'
    return f'役職 {arg} は存在しません'
