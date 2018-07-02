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
    await client.create_role(message.server, name=arg, mentionable=True)
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


async def run_command(message):
    msg = ''
    remark = message.content
    if remark == '/role':
        role_names = get_role_names(message.server.roles, is_common)
        msg = 'このサーバーにある役職は以下の通りです\n' + \
            ', '.join(role_names) if role_names else '役職がありません'
    if remark.startswith('/role '):
        msg = await set_roles(message)
    if remark == '/role_self':
        role_names = [role.name[1:]
                      for role in message.author.roles if not role.is_everyone]
        msg = ', '.join(role_names) if role_names else '役職が設定されていません'
    if remark.startswith('/create_role '):
        msg = await requires_admin(message, create_role)
    if remark.startswith('/delete_role '):
        msg = await requires_admin(message, delete_role)
    if remark == '/debug_on':
        msg = toggle_debug_mode(True)
    if remark == '/debug_off':
        msg = toggle_debug_mode(False)
    if msg:
        mention = str(message.author.mention) + ' '
        await client.send_message(message.channel, mention + msg)


@client.event
async def on_ready():
    print('Logged in')


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
