def command_db(r, msg):
    """
    /db key
    /db key value
    /db -list
    /db -delete key
    /db -delete key value
    """
    args = msg.content.split()
    id = msg.author.id
    if len(args) == 2:
        if args[1] == '-list':
            return get_keys(r, id)
        else:
            return get_values(r, id, args[1])
    elif len(args) == 3:
        if args[1] == '-delete':
            return del_key(r, id, args[2])
        else:
            return set_value(r, id, args[1], args[2])
    elif len(args) == 4:
        if args[1] == '-delete':
            return del_value(r, id, args[2], args[3])
        else:
            '不正な形式です。'
    else:
        return '不正な形式です。'


def get_keys(r, id):
    if r.exists(id):
        data = r.smembers(id)
        return normalize(data)
    return 'データが存在しません。'


def get_values(r, id, k):
    key = f'{id}:{k}'
    if r.exists(key):
        data = r.smembers(key)
        return normalize(data)
    return f'{k} は存在しません。'


def set_value(r, id, k, v):
    r.sadd(f'{id}:{k}', v)
    r.sadd(id, k)
    return f'{k} に {v} を追加しました。'


def del_key(r, id, k):
    key = f'{id}:{k}'
    if r.exists(key):
        r.delete(key)
        r.srem(id, k)
        return f'{k} を削除しました。'
    return f'{k} は存在しません。'


def del_value(r, id, k, v):
    key = f'{id}:{k}'
    if r.exists(key):
        r.srem(key, v)
        return f'{k} から {v} を削除しました。'
    return f'{k} は存在しません。'


def normalize(data):
    return ' '.join(sorted([d.decode() for d in data]))
