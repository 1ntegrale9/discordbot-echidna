import redis
import os

ID_DEVELOPER = 314387921757143040
r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)


def knowledge(message):
    args = message.content.split()
    if len(args) == 3 and args[1] == '教えて':
        key = f'{message.guild.id}:{args[2]}'
        if r.exists(key):
            return f'{args[2]} は {r.get(key)}'
        else:
            return '？'
    elif len(args) == 4 and args[1] == '覚えて':
        key = f'{message.guild.id}:{args[2]}'
        r.set(key, args[3])
        r.sadd(message.guild.id, args[2])
        return f'{args[2]} は {args[3]}、覚えました！'
    else:
        return '？'


async def command_db(msg, bot):
    """
    /db Key
    /db Key Value
    /db -help
    /db -flushall
    /db -flushdb
    /db -list
    /db -all
    /db -delete Key
    /db -delete Key Value
    """
    args = msg.content.split()
    id = msg.server.id
    if len(args) == 2:
        if args[1] == '-help':
            return help()
        if args[1] == '-list':
            return smembers_keys(id)
        if args[1] == '-all':
            if msg.author.id == ID_DEVELOPER:
                return await keys(bot)
            return '開発者のみ実行可能なコマンドです。'
        if args[1] == '-flushall':
            if msg.author.id == ID_DEVELOPER:
                return flushall()
            return '開発者のみ実行可能なコマンドです。'
        if args[1] == '-flushdb':
            if msg.author.id == ID_DEVELOPER:
                return flushdb()
            return '開発者のみ実行可能なコマンドです。'
        else:
            return smembers_values(id, args[1])
    elif len(args) == 3:
        if args[1] == '-delete':
            return srem_key(id, args[2])
        else:
            return sadd_value(id, args[1], args[2])
    elif len(args) == 4:
        if args[1] == '-delete':
            return srem_value(id, args[2], args[3])
        else:
            '不正な形式です。'
    else:
        return '不正な形式です。'


def smembers_keys(id):
    if r.exists(id):
        data = r.smembers(id)
        return normalize(data)
    return 'データが存在しません。'


def smembers_values(id, k):
    key = f'{id}:{k}'
    if r.exists(key):
        data = r.smembers(key)
        return normalize(data)
    return f'{k} は存在しません。'


def sadd_value(id, k, v):
    r.sadd(f'{id}:{k}', v)
    r.sadd(id, k)
    return f'{k} に {v} を追加しました。'


def srem_key(id, k):
    key = f'{id}:{k}'
    if r.exists(key):
        r.delete(key)
        r.srem(id, k)
        return f'{k} を削除しました。'
    return f'{k} は存在しません。'


def srem_value(id, k, v):
    key = f'{id}:{k}'
    if r.exists(key):
        r.srem(key, v)
        return f'{k} から {v} を削除しました。'
    return f'{k} は存在しません。'


def flushall():
    r.flushall()
    return 'Deleted all keys in all databases on the current host.'


def flushdb():
    r.flushdb()
    return 'Deleted all keys in the current database.'


def help():
    return '後で書く'


def normalize(data):
    return '\n'.join(sorted(data))


async def keys(bot):
    for key in sorted(r.keys()):
        await bot.get_user(ID_DEVELOPER).send(key)
    return 'リストをDMに送信しました。'
