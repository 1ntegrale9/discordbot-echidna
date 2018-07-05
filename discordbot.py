from random import randint
import os
import traceback
import discord

client = discord.Client()
debug_mode = False


async def requires_admin(message, func):
    if message.author.server_permissions.administrator:
        return await func(message)
    return 'コマンドを実行する権限がありません'


async def create_role(message):
    arg = message.content.split('/create_role ')[1]
    if arg.lower() in [role.name.lower() for role in message.server.roles]:
        return 'その役職は既に存在します'
    await client.create_role(
        message.server,
        name=arg,
        mentionable=True,
        color=discord.Colour(generate_random_color()),
    )
    return '役職 {} を作成しました'.format(arg)


async def delete_role(message):
    arg = message.content.split('/delete_role ')[1].lower()
    role_names = [role.name.lower() for role in message.server.roles]
    if arg in role_names:
        index = role_names.index(arg)
        role = message.server.roles[index]
        await client.delete_role(message.server, role)
        return '役職 {} を削除しました'.format(role.name)
    return '役職 {} は存在しません'.format(arg)


def toggle_debug_mode(mode):
    global debug_mode
    debug_mode = mode
    return 'デバッグモードを{}にしました'.format('ON' if mode else 'OFF')


async def set_roles(message):
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


def is_common(role):
    if role.is_everyone:
        return False
    if role.managed:
        return False
    if role.permissions.administrator:
        return False
    return True


def get_role_names(roles, requirements):
    return [r.name for r in roles if requirements(r)]


def generate_random_color():
    rgb = [randint(0, 255) for _ in range(3)]
    return int('0x{:X}{:X}{:X}'.format(*rgb), 16)


def get_help():
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
        '`/debug_on`':
            'エラー時にスタックトレースを出力します',
        '`/debug_off`':
            'エラー時にエラーメッセージを出力します',
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


async def run_command(message):
    msg, embed = None, None
    remark = message.content
    if remark == '/role':
        role_names = get_role_names(message.server.roles, is_common)
        msg = 'このサーバーにある役職は以下の通りです\n' + \
            ', '.join(role_names) if role_names else '役職がありません'
    if remark.startswith('/role '):
        msg = await set_roles(message)
    if remark == '/role_self':
        role_names = get_role_names(message.author.roles, is_common)
        msg = ', '.join(role_names) if role_names else '役職が設定されていません'
    if remark.startswith('/create_role '):
        msg = await requires_admin(message, create_role)
    if remark.startswith('/delete_role '):
        msg = await requires_admin(message, delete_role)
    if remark == '/member':
        arg = message.server.member_count
        msg = 'このサーバーには{}人のメンバーがいます'.format(arg)
    if remark == '/debug_role':
        embed = discord.Embed(title="role name", description="role id")
        for role in message.server.roles:
            embed.add_field(name=role.name, value=role.id, inline=False)
    if remark == '/debug_on':
        msg = toggle_debug_mode(True)
    if remark == '/debug_off':
        msg = toggle_debug_mode(False)
    if remark == '/help':
        embed = get_help()
    if msg:
        mention = str(message.author.mention) + ' '
        await client.send_message(message.channel, mention + msg)
    if embed:
        await client.send_message(
            message.channel,
            message.author.mention,
            embed=embed
        )


@client.event
async def on_ready():
    print('Logged in')
    await client.edit_profile(username="Echidna")

@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return
        else:
            await run_command(message)
    except Exception as e:
        await client.send_message(message.channel, str(e))
        if debug_mode:
            traceback_msg = '```\n{}\n```'.format(traceback.format_exc())
            await client.send_message(message.channel, traceback_msg)
    else:
        pass
    finally:
        pass

client.run(os.environ['DISCORD_BOT_TOKEN'])
