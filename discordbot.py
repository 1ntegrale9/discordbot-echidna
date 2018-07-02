import os
import traceback
import discord
from module.role import requires_admin
from module.role import create_role
from module.role import delete_role
from module.role import set_roles
from module.role import is_common
from module.role import get_role_names

client = discord.Client()
debug_mode = False


def toggle_debug_mode(mode):
    global debug_mode
    debug_mode = mode
    return 'デバッグモードを{}にしました'.format('ON' if mode else 'OFF')


async def run_command(message):
    msg = ''
    remark = message.content
    if remark == '/role':
        role_names = get_role_names(message.server.roles, is_common)
        msg = 'このサーバーにある役職は以下の通りです\n' + \
            ', '.join(role_names) if role_names else '役職がありません'
    if remark.startswith('/role '):
        msg = await set_roles(client, message)
    if remark == '/role_self':
        role_names = get_role_names(message.author.roles, is_common)
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
