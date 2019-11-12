import string
from random import randint
from random import shuffle
from random import choices


def generate_random_token():
    length = (24, 34)
    strings = choices(string.ascii_letters + string.digits, k=sum(length))
    strings.insert(length[0], '.')
    return ''.join(strings)


def generate_random_color() -> int:
    """カラーコードを10進数で返す"""
    rgb = [randint(0, 255) for _ in range(3)]
    return int('0x{:X}{:X}{:X}'.format(*rgb), 16)


def get_role_names(roles):
    return sorted([role.name for role in roles if not role.is_default()])


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
        if len(g) < n - 1:
            g.append(m)
        else:
            g.append(m)
            tmp = ' '.join(g)
            groups.append(f'{(i+1)//n}班 {tmp}')
            g = []
    if rest:
        groups.append('余り {}'.format(' '.join(rest)))
    return '\n'.join(groups)
