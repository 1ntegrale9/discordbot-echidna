import asyncio, discord, os, traceback

client = discord.Client()
debug_mode = False

@client.event
async def on_ready():
    print('Logged in')

@client.event
async def on_message(message):
    try:
        global debug_mode
        if message.author == client.user:
            return
        else:
            msg = ''
            remark = message.content
            if remark.startswith('/role'):
                if remark.startswith('/role '):
                    add, rm, pd, nt = [], [], [], []
                    role_names = [role.name for role in message.server.roles]
                    for role_name in remark.split()[1:]:
                        if role_name in role_names:
                            index = role_names.index(role_name)
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
                else:
                    role_names = [role.name for role in message.server.roles if not (role.is_everyone or role.managed or role.permissions.administrator)]
                    msg = 'このサーバーにある役職は以下の通りです\n' + ', '.join(role_names) if role_names else '役職がありません'
            if remark == '/self role':
                role_names = [role.name[1:] for role in message.author.roles if not role.is_everyone]
                msg = ', '.join(role_names) if role_names else '役職が設定されていません'
            if remark == '/debug true':
                debug_mode = True
            if remark == '/debug false':
                debug_mode = False
            if msg:
                mention = str(message.author.mention) + ' '
                await client.send_message(message.channel, mention + msg)
    except Exception as e:
        await client.send_message(message.channel, str(e))
        if debug_mode:
            await client.send_message(message.channel, '```\n{}\n```'.format(traceback.format_exc()))
    else:
        pass
    finally:
        pass

client.run(os.environ['DISCORD_BOT_TOKEN'])
