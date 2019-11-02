from attrdict import AttrDict


def get_id():
    return AttrDict({
        'user': {
            'developer': 314387921757143040,
        },
        'channel': {
            'login': 502837677108887582,
            'debug': 577028884944388107,
            'traceback': 502901411445735435,
            'question': 575870793888694274,
        },
        'category': {
            'private': 361479341256998914,
            'free': 548777809343021056,
            'musicbot': 548752809965781013,
            'issues': 575935336765456394,
            'closed': 640090897417240576,
        },
        'guild': {
            'bot': 494911447420108820,
            'werewolf': 307721817563594753,
        },
    })


def get_close_keyword():
    return [
        'close',
        'closes',
        'closed',
        'fix',
        'fixes',
        'fixed',
        'resolve',
        'resolves',
        'resolved',
    ]
